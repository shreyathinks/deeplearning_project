import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights

class SeverityClassifier(nn.Module):
    def __init__(self, num_classes=3, num_engineered_features=9):
        super(SeverityClassifier, self).__init__()
        
        # Pretrained ResNet18 backbone
        self.backbone = resnet18(weights=ResNet18_Weights.DEFAULT)
        
        # Remove the final classification layer
        # The output of resnet18 before fc is 512 dimensions
        self.cnn_features_dim = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        
        # MLP for classification combining CNN and engineered features
        self.mlp = nn.Sequential(
            nn.Linear(self.cnn_features_dim + num_engineered_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
        
    def forward(self, image, engineered_features):
        """
        image: (B, C, H, W) tensor of the damage-focused image
        engineered_features: (B, F) tensor of numerical features derived from bbox/masks
        """
        # Get CNN features
        cnn_out = self.backbone(image)
        
        # Concatenate
        combined = torch.cat((cnn_out, engineered_features), dim=1)
        
        # Predict severity
        logits = self.mlp(combined)
        return logits
