import torch
from torch import nn
import pytorch_lightning as pl
from typing import Tuple


class VAE(pl.LightningModule):
    """
    A Variational Autoencoder (VAE) implemented using PyTorch Lightning.

    This module is designed to learn a latent representation of the input data,
    typically for dimensionality reduction, generative modeling, or other tasks
    in unsupervised learning.

    Attributes:
        input_dim (int): The input dimension of the data.
        hidden_dim (int): The dimension of the hidden layers.
        latent_dim (int): The dimension of the latent space.
        learning_rate (float): The learning rate for the optimizer.
    """

    def __init__(
        self,
        input_dim: int = 784,
        hidden_dim: int = 400,
        latent_dim: int = 200,
        learning_rate: float = 0.001,
    ):
        super(VAE, self).__init__()
        self.save_hyperparameters()
        self.lr = learning_rate

        # Encoder part of the VAE
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(0.2),
        )

        # Latent mean and variance layers
        self.mean_layer = nn.Linear(hidden_dim, latent_dim)
        self.logvar_layer = nn.Linear(hidden_dim, latent_dim)

        # Decoder part of the VAE
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid(),
        )

    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encodes the input data into the latent space representation.

        Args:
            x (torch.Tensor): The input tensor.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: A tuple containing the mean and
                log variance of the latent space representation.
        """
        x = self.encoder(x)
        mean, logvar = self.mean_layer(x), self.logvar_layer(x)
        return mean, logvar

    def reparameterization(
        self, mean: torch.Tensor, logvar: torch.Tensor
    ) -> torch.Tensor:
        """
        Performs the reparameterization trick to sample from the latent space.

        Args:
            mean (torch.Tensor): The mean of the latent space.
            logvar (torch.Tensor): The log variance of the latent space.

        Returns:
            torch.Tensor: Sampled latent vector.
        """
        epsilon = torch.randn_like(logvar)
        z = mean + torch.exp(logvar / 2) * epsilon
        return z

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """
        Decodes the latent space representation back into the input space.

        Args:
            z (torch.Tensor): The latent vector.

        Returns:
            torch.Tensor: The decoded tensor.
        """
        return self.decoder(z)

    def forward(
        self, batch: Tuple[torch.Tensor, torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        The forward pass of the VAE.

        Args:
            batch (List[torch.Tensor]): The input batch.

        Returns:
            Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
                Tuple containing original input, reconstructed input, mean, and
                log variance.
        """
        x, _ = batch
        x = x.view(x.shape[0], -1)
        mean, logvar = self.encode(x)
        z = self.reparameterization(mean, logvar)
        x_hat = self.decode(z)
        return x, x_hat, mean, logvar

    def loss_function(
        self,
        x: torch.Tensor,
        x_hat: torch.Tensor,
        mean: torch.Tensor,
        logvar: torch.Tensor,
    ) -> torch.Tensor:
        """
        Calculates the loss function for the VAE, comprising both the
        reconstruction loss and the KL divergence.

        Args:
            x (torch.Tensor): The original input.
            x_hat (torch.Tensor): The reconstructed input.
            mean (torch.Tensor): The mean of the latent space.
            logvar (torch.Tensor): The log variance of the latent space.

        Returns:
            torch.Tensor: The computed loss.
        """
        reproduction_loss = nn.functional.binary_cross_entropy(
            x_hat, x, reduction="sum"
        )
        KLD = -0.5 * torch.sum(1 + logvar - mean.pow(2) - logvar.exp())
        return reproduction_loss + KLD

    def training_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> torch.Tensor:
        """
        Performs a training step.

        Args:
            batch (Tuple[torch.Tensor, torch.Tensor]): The input batch.
            batch_idx (int): The index of the batch.

        Returns:
            torch.Tensor: The loss for this training step.
        """
        x, x_hat, mean, logvar = self.forward(batch)
        loss = self.loss_function(x=x, x_hat=x_hat, mean=mean, logvar=logvar)
        self.log("train_loss", loss, prog_bar=True)
        return loss

    def validation_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> torch.Tensor:
        """
        Performs a validation step.

        Args:
            batch (Tuple[torch.Tensor, torch.Tensor]): The input batch.
            batch_idx (int): The index of the batch.

        Returns:
            torch.Tensor: The loss for this validation step.
        """
        x, x_hat, mean, logvar = self.forward(batch)
        loss = self.loss_function(x=x, x_hat=x_hat, mean=mean, logvar=logvar)
        self.log("val_loss", loss, prog_bar=True)
        return loss

    def configure_optimizers(self) -> torch.optim.Optimizer:
        """
        Configures the optimizer for the VAE.

        Returns:
            torch.optim.Optimizer: The configured optimizer.
        """
        return torch.optim.Adam(self.parameters(), lr=self.lr)
