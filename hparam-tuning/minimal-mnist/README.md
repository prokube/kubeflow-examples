# Minimal Katib Example Using scikit-learn and MNIST

This example demonstrates the use of Katib for hyperparameter tuning with a 
simple scikit-learn model trained on the MNIST dataset.

## Steps
Generally, the following four steps are required to run a hyperparameter tuning 
experiment using custom training code. However, Steps 1 and 2 are covered in 
the corresponding image directory `./images/minimal-mnist/`:
1. Write the training code.
2. Create a Dockerfile for the training environment.
3. Build the training image.
4. Define the experiment YAML file for the Katib experiment.

For building the image (Step 3), instructions are available in the same 
directory.

For Step 4, you can use the example provided in this directory.

## Starting the Experiment
To start the Katib experiment, modify the `image` entry in the YAML file. 
You can either modify the file directly and run:

```sh
kubectl create -f katib-experiment.yaml -n <your-namespace>
```

Or use the following command to modify it while starting the experiment:

```sh
sed 's/MNIST-IMAGE/<your-image-path>/' katib-experiment.yaml | kubectl create -f - -n <your-namespace>
```

## Deleting the Experiment
To delete the experiment from your Kubernetes cluster, run:

```sh
kubectl delete -f katib-experiment.yaml
```
