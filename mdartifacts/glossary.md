# 📖 Dysgraphia & Machine Learning Glossarium

A quick reference guide to the medical and technical terms used in the automated assessment of handwriting disorders.

## 🩺 Clinical Terms

* **Dysgraphia**: A neurodevelopmental learning disability that affects a child's ability to produce readable, organized, and linguistically coherent handwriting.
* **Motor Dysgraphia**: A subtype of dysgraphia caused by fine motor coordination deficits. Characterized by low stroke velocity, excessive pen pressure, and abnormal grip tension.
* **Spatial Dysgraphia**: A subtype characterized by a lack of visuospatial organization. Manifests as high spacing variance, severe alignment deviation, and irregularly positioned text, despite normal writing speed.
* **Dyslexic Dysgraphia**: A subtype rooted in language-cognitive deficits, such as poor phonological processing and orthographic coding, rather than impaired motor execution.
* **Kinematics**: The study of motion. In handwriting, it refers to the dynamic aspects of the writing process, such as stroke velocity, pen pressure, and movement smoothness.
* **Visuospatial Organization**: The cognitive ability to perceive and manage spatial relationships, translating into consistent letter alignment, spacing, and page layout.

## 💻 Machine Learning Terms

* **Early Fusion**: A multimodal data integration strategy where features from different modalities (e.g., online kinematic data and offline image data) are concatenated *before* being fed into a machine learning classifier.
* **Online Handwriting Features**: Data captured dynamically while the subject is writing, including time-stamped pen trajectories, pressure, and speed.
* **Offline Handwriting Features**: Static visual features extracted from the final written image, such as character shape, slant, and geometric alignment.
* **Dual-Stream Architecture**: A deep learning model design that processes two different types of inputs in parallel (e.g., a CNN for static images and a Trajectory-Transformer for dynamic movements) before combining them.
* **Grad-CAM (Gradient-weighted Class Activation Mapping)**: An explainable AI technique that produces visual heatmaps over input images, highlighting the specific regions that most heavily influenced the model's classification decision.
* **t-SNE (t-Distributed Stochastic Neighbor Embedding)**: A dimensionality reduction technique used to visualize high-dimensional data in 2D or 3D plots, commonly used to show how well a model separates different classes (e.g., dysgraphic vs. typical).
* **XGBoost (Extreme Gradient Boosting)**: A highly efficient and scalable machine learning algorithm that uses an ensemble of decision trees to improve predictive performance.
* **SVM (Support Vector Machine)**: A supervised learning algorithm that finds the optimal hyperplane to separate different classifications in high-dimensional space.
