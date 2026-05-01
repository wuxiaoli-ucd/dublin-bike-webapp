**Generative AI chats \- Xiaoli Wu**

# 1.Github

**Question:** How should we organise the GitHub structure for this project?

**Answer:** A clear GitHub structure should separate the main parts of the project, such as frontend, backend, scraper, and machine learning components. This makes the repository easier to maintain and allows team members to work on different modules with less interference. Supporting files such as README, requirements, and environment configuration should also be clearly organised.

**Question:** Can I pull only one file from another Git branch instead of merging the entire branch?

**Answer:** Yes, it is possible to retrieve a specific file from another branch using Git commands. This allows selective updates without merging all changes.

**Question:** Why is it important to use a .env file in this project?

**Answer:** A .env file allows sensitive information such as API keys and database credentials to be stored securely outside the codebase. This prevents accidental exposure when pushing code to GitHub and makes it easier to manage different environments.

**Question:** GitHub has a file size limit. What should I do if my model file is too large to upload?

**Answer:** GitHub typically has a file size limit (e.g., 100MB per file). If a model file exceeds this limit, it is recommended not to upload the file directly. Instead, the project should include the code required to generate the model, and instructions for reproducing it locally. This ensures that the repository remains lightweight and maintainable.

# 2\. EC2 & RDS deployment

**Question:** Why does my Flask server stop running after I close the terminal on EC2?

**Answer:** By default, processes started in a terminal session will stop when the session is closed. To keep the server running, tools such as nohup or process managers can be used to run the application in the background.

**Question:** Can I remotely connect to my RDS database to view and query the data?

**Answer:** Yes, it is possible to connect to an RDS database remotely, provided that the correct configuration is in place. The database must allow external access, and the user must have the necessary credentials. Tools such as database clients can then be used to connect and query the data.

**Question:** Why am I unable to connect to my RDS database from my local machine?

**Answer:** This is often due to security restrictions. Common issues include:

* The security group does not allow inbound traffic from the user’s IP address  
* The database is not publicly accessible  
* Incorrect credentials or endpoint configuration  
   Checking these settings usually resolves the issue.

# 3\. Machine Learning

**Question:** In random forest, how should I decide which features to include? Should I rely on correlation analysis?

**Answer:** Correlation analysis is mainly useful for linear models, but it is not always suitable for tree-based models such as Random Forest. Random Forest can capture non-linear relationships and interactions between features, so even variables with low correlation may still be useful. A practical approach is to start with a broad set of features, train the model, evaluate feature importance, and then iteratively remove less important features.

**Question:** Weather variables seem to have low importance. Should I remove them?

**Answer:** If weather variables consistently show low importance and do not improve validation performance, they can be removed to simplify the model. However, it is recommended to first compare model performance with and without these variables, and also consider whether weather may still have an impact in certain real-world scenarios.

**Question:** Is there a difference in feature selection between linear models and tree-based models?

**Answer:** Yes. Linear models rely more on linear relationships, so feature selection often depends on correlation and assumptions about linearity. Tree-based models, such as Random Forest, are more flexible and can handle non-linear relationships and interactions, so they usually require less strict feature selection at the beginning.

**Question:** Should the model generate predictions for the next 8 hours in the backend, or should the frontend call the model multiple times?

**Answer:** Both approaches are possible. Generating predictions in the backend provides a cleaner API and is more efficient, while calling the model multiple times from the frontend is simpler and more flexible. For initial implementation, calling the model multiple times is usually easier, with backend optimisation added later if needed.

**Question:** Why did Gradient Boosting perform worse than Random Forest in my case?

**Answer:** Gradient Boosting is more sensitive to hyperparameters and can overfit if not properly tuned. It may also require more careful preprocessing and parameter adjustment. Random Forest is generally more robust and easier to tune, which often leads to better performance in initial implementations.

**Question:** Should station\_mean be a fixed value or updated over time?

**Answer:** station\_mean should ideally be updated based on the most recent available data. Using a fixed value based on historical data may reduce model accuracy over time, especially if usage patterns change. A dynamic update mechanism would better reflect real-world conditions.

**Question:** When building a prediction model, should I focus on predicting a single time point or a time range?

**Answer:** This depends on the application. For real-time systems, predicting a single time point is often sufficient and more efficient. Predicting a time range requires more complex models and higher computational cost, so it should only be implemented if there is a clear user requirement.

