import click
import pytorch_lightning as pl
from pytorch_lightning.plugins.environments import KubeflowEnvironment
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from model.vae import VAE
from model.datamodule import MNISTDataModule
import torch
import mlflow
import mlflow.pytorch
import os
import logging

logger = logging.getLogger(__name__)


@click.command()
@click.option('--hidden-dim', default=400, type=int, help='Dimension of the hidden layer.')
@click.option('--latent-dim', default=2, type=int, help='Dimension of the latent space.')
@click.option('--batch-size', default=32, type=int, help='Batch size for training.')
@click.option('--lr', default=1e-3, type=float, help='Learning rate.')
@click.option('--max-epochs', default=10, type=int, help='Maximum number of epochs.')
@click.option('--seed', default=42, type=int, help='Random seed.')
@click.option('--run-as-pytorchjob', is_flag=True, help='Run as PyTorch job in Kubeflow.')
@click.option('--mlflow-uri', default='file:./mlruns', help='MLflow tracking URI (default: local file system).')
@click.option('--mlflow-experiment-name', default='mnist-vae', help='MLflow experiment name.')
@click.option('--run-name', default=None, help='MLflow run name.')
def run_training(
    hidden_dim: int,
    latent_dim: int,
    batch_size: int,
    lr: float,
    max_epochs: int,
    seed: int,
    run_as_pytorchjob: bool,
    mlflow_uri: str,
    mlflow_experiment_name: str,
    run_name: str
) -> None:
    """
    Train a VAE model on the MNIST dataset using PyTorch Lightning with MLflow logging.
    
    This example demonstrates:
    a) PyTorch Lightning training
    b) MLflow logging
    c) PyTorchJob (distributed training in Kubeflow)
    """
    # Determine accelerator
    accelerator = "gpu" if torch.cuda.is_available() else "cpu"
    
    # Initialize data module
    dm = MNISTDataModule(
        data_path="./data", 
        num_workers=4 if not run_as_pytorchjob else 0,  # Reduce workers for distributed
        batch_size=batch_size
    )
    dm.setup()
    
    # Initialize model
    model = VAE(
        input_dim=784,  # 28x28 pixels
        hidden_dim=hidden_dim,
        latent_dim=latent_dim,
        learning_rate=lr
    )
    
    # Setup callbacks
    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            mode="min",
            patience=5,
            strict=True,
        ),
        ModelCheckpoint(
            monitor="val_loss",
            mode="min",
            save_top_k=1,
            filename="best-model-{epoch:02d}-{val_loss:.2f}",
        )
    ]
    
    # Initialize trainer
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        accelerator=accelerator,
        devices=1,
        callbacks=callbacks,
        plugins=[KubeflowEnvironment()] if run_as_pytorchjob else [],
        strategy="ddp" if run_as_pytorchjob else "auto",
        enable_progress_bar=not run_as_pytorchjob,  # Disable progress bar for distributed
        log_every_n_steps=10,
        logger=False,  # Disable default logger since we use MLflow
    )
    
    # Log trainer info for debugging
    if run_as_pytorchjob:
        logger.info(f"Running as PyTorchJob - Global rank: {trainer.global_rank}")
        logger.info(f"Trainer strategy: {trainer.strategy}")
    
    # Only setup MLflow on the master process (rank 0)
    if not run_as_pytorchjob or trainer.global_rank == 0:
        logger.info("Setting up MLflow logging...")
        
        # Configure MLflow
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment(mlflow_experiment_name)
        
        # Enable MLflow autologging
        mlflow.pytorch.autolog(log_models=True)
        
        # Start MLflow run
        with mlflow.start_run(run_name=run_name):
            # Log hyperparameters
            mlflow.log_params({
                "hidden_dim": hidden_dim,
                "latent_dim": latent_dim,
                "batch_size": batch_size,
                "learning_rate": lr,
                "max_epochs": max_epochs,
                "seed": seed,
                "accelerator": accelerator,
                "distributed": run_as_pytorchjob
            })
            
            # Train the model
            trainer.fit(model=model, datamodule=dm)
            
            # Log final metrics
            if trainer.checkpoint_callback.best_model_path:
                mlflow.log_artifact(trainer.checkpoint_callback.best_model_path)
                logger.info(f"Best model saved: {trainer.checkpoint_callback.best_model_path}")
            
            # Get run info
            run_info = {
                "run_id": mlflow.active_run().info.run_id,
                "best_val_loss": trainer.checkpoint_callback.best_model_score.item(),
                "status": "success
            }
            
            logger.info(f"Training completed. Run ID: {run_info['run_id']}")
            return run_info
    
    else:
        # Worker processes just train without MLflow
        logger.info(f"Worker process (rank {trainer.global_rank}) - training without MLflow")
        trainer.fit(model=model, datamodule=dm)


if __name__ == "__main__":
    run_training()
