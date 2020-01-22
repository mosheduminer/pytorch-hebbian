import logging

import torch
from torch.nn import Module
from torch.utils.data import DataLoader
from tqdm import tqdm

import config
from pytorch_hebbian.learning_engines.learning_engine import LearningEngine


class SupervisedEngine(LearningEngine):

    def __init__(self, criterion, optimizer, lr_scheduler=None, evaluator=None):
        super().__init__(optimizer, lr_scheduler, evaluator)
        self.criterion = criterion
        self.losses = []

    def _train_step(self, model, inputs, labels):
        inputs = inputs.to(self.device).view(inputs.size(0), -1)
        labels = labels.to(self.device)

        # Zero the parameter gradients
        self.optimizer.zero_grad()

        # Calculate the loss
        outputs = model(inputs)
        _, predictions = torch.max(outputs, 1)
        loss = self.criterion(outputs, labels)

        # Back propagation and optimize
        loss.backward()
        self.optimizer.step()

        return loss

    def train(self, model: Module, data_loader: DataLoader, epochs: int,
              eval_every: int = None, checkpoint_every: int = None):
        model.train()

        # Training loop
        for epoch in range(epochs):
            vis_epoch = epoch + 1
            running_loss = 0.0

            # learning_rates = [param_group['lr'] for param_group in self.optimizer.param_groups]
            # logging.info("Learning rate(s) = {}.".format(learning_rates))

            progress_bar = tqdm(data_loader, desc='Epoch {}/{}'.format(vis_epoch, epochs),
                                bar_format=config.TQDM_BAR_FORMAT)
            for inputs, labels in progress_bar:
                loss = self._train_step(model, inputs, labels)

                # Statistics
                running_loss += loss.item() * inputs.size(0)

            if self.lr_scheduler is not None:
                self.lr_scheduler.step()

            epoch_loss = running_loss / len(data_loader.dataset)
            self.losses.append(epoch_loss)
            logging.info('Train loss: {:.4f}'.format(epoch_loss))

            # TODO save or return best model

            # Evaluation
            stats = None
            if eval_every is not None:
                if vis_epoch % eval_every == 0:
                    stats = self.eval()

            # Checkpoint saving
            if checkpoint_every is not None:
                if vis_epoch % checkpoint_every == 0:
                    if stats is not None:
                        self.checkpoint(model, stats=stats)
                    else:
                        self.checkpoint(model)

        return model