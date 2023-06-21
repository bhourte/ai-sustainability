# ai-sustainability

## Objective of the project
The objective of this project is to set up a guideline for the design of AI models from the client expectation to the finished product. And this is the work we have done so far :
## The 4 parts :
### 1. The Form
The first part we worked on was the creation of an UI app to retrieve the requirements of a client by asking specific questions. This app contains a form that can be completed by a user. This form then gives a list of AI models that would be most likely to fit and creates an MlFlow experiment linked to the filled form where the data scientist can record the results of the tests they will perform in Part 2.  
This app comes with 5 pages :  
- Connection : The page where the user can connect himself with is id.
- Form : The page where the user/client can fill a form and this page give him de best possible models and create an MlFlow experiment (if the mlflow server is running).
- History : The page where the user and/or the Admin can see a previous completed form and where he can make changes in it (if changes are made, a new list of best possible AI will be given).
- Feedback : The page where the user can give feedback and where the Admin can see all given feedback.
- Statistic : The page where the Admin can see which choices are most often selected by users.
### 2. The template
The second part we worked on was a fillable template that the data scientist can use to run many tests with many different models with different hyperparameters.  
This template must be linked with the MlFlow experiement created by the first part in order to log all models with the corresponding metrics (so the MlFlow server must be running).
### 3. The evaluation tool
***Only works if the MlFlow server is running***  
The third part we worked on was an evaluation tool app which allows the data scientist to compare the different models tested in part 2 to find the one that best meets their expectations.  
This app comes with 7 pages :
- Experiment selection : The page where the user can select the MlFlow experiment he wants to evaluate.
- Ranking : The page where the user can rank all tested models according to the metrics he wants.
- Pareto graph : The page where the user can plot a graph where all models are compared according to 2 metrics and the pages give all best models according these 2 metrics (models on the parto's frontier).
- Spider graph : The page where the user can select several metrics to compare several models according to their area represented on the graph.
- Confusion matrix : The page where the user can see all the confusion matrix for all models in order to compare the rate of false negative and false positive.  
  *Only work for binary classification models*
- Artifacts : The page where the user can see all artifact log in the MlFlow experiment for all models and where he can compare model's artifact side-by-side.
- Form : The page where the user can see a previous completed form (from the first part of the project) to have the list of aswer given by the client.
### 4. The quality chek-list
The last (but not least) part we worked on was an app where the datascientist can see all the elements that its AI project must contain to have sufficient quality in the business world.  
This app comes with 7 pages which have a checklist : 
- Global quality check : The page where the user can see a summary of all score obtained on the other page and a global score on how good his model is.
- Dataset : The checklit page where the user can see all action he need to do with the colected data.
- Pipeline : The checklit page where the user can see all action the pipeline of his model must have.
- Model selection : The checklit page where the user can see all action he need to do when he select the best model (in the second and thirdpart).
- Performance : The checklit page where the user can see all action he need to do when he evaluates his model.
- Documentation : The checklit page where the user can see all information he need to put in the documentation of his project.
- Deployment : The checklit page where the user can see all action he need to do when he will deploy his model.  


## How to launch?
For now on, all part can be launch independently, but in the future they will be comprised in a single app.

1. The Form part : The user can launch the Form part with the **start_form.ps1** file a powershell terminal.
2. The Template part : The user have a template to fill (this is an jupyter notebook) and to execute. He must fill all element with "**...**" and **TODO** and have a running MlFlow server.
3. The Evaluation Tool part : To launch the evaluation tool, the user can simply execute the **start_validation.ps1** file in a powershell terminal.
4. The Checklist part : To launch the evaluation tool, the user can simply execute the **start_checklist.ps1** file in a powershell terminal.
5. The MlFlow server : Part 1, 2 and 3 need to have a running MlFlow server to accomplish their tasks. The user can launch any mlflow server (on the port specified in the .env file), but it is recomended to launche the mlflow server with the **start_mlflow.ps1** powrshell file.

Work Done by Hennecart Alexandre and Filee Arnauld