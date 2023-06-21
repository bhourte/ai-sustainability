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

## How does it work?
In order to make all the elements work, we had to put in place several things:
1. An Gremlin database deployed on Azure Cosmos DB : we stored the graph with all question-answer in a Gremlin graph db on the cloud (on Azure). This database also store all completed form and all given feedback. It is used by the Form part and the Evaluation Tool part
2. An mlflow server : part 1 to 3 need a running MlFlow server to operate (Form, to create the experiment, Template to fill it with logs and the Tool to retreive metrics). We usualy store all experiment/artifact directly in the ai-sutainability fodler, but this is not required.
3. A local SQL database to store all element needed by the check-list.

## How elements are stored in the 2 databases :
### Gremlin DB :
The Gremlin DB is used only by the part 1 (the Form) and just a little bit by the evaluation tools (retreive the list of all user and show a previous answered Form)  
In the Gremlin DB, we store element in 2 form : node and edge (just like a graph, because this is a graph). A Node = a question in the Form and an edge = a (possible) answer in the form.  
Each question-node has : 
- id : the number of the question
- label : the label of the question, one label = one type (Q_QCM, Q_Open, Q_QRM, end). The "end" label is the label for the last element, this is not a question, but each edges need to arrive to a final node, and this is the node.
- text : the text of the question
- help text : the help text of the question (a small explaination of the question and why we ask it)
- list_AI (only for node with id==1) : the list of all existing AI in the Form

Each answer-edge has :
- id : id of the edge (create as : node_in_node_out_number)
- label : Proposition (for edge in the possible answers) or Answer (for selected answer in a stored completed form)
- text : text of the answer
- help text : a text to help to understand the answer
- modif_crypted : if the answer is modified with encrypted data (special case)
- list_coef : the list of all coefficient for each AI  

But there is other type of node :
1. User node : a node corresponding to an user (with id=username, label==user)
2. Feedback node : a node that store a feedback of a user (the edge between a feedback node and a User node has label=Feedback)
3. Answer node : node exactly like question-node, but with only 1 edge in and 1 edge out (the selected answers). And the first node of the form (the node corresponding to question 1) has a best_ais property corresponding to the calculeted best AI when the user has filled the form

## How to update?
To update the element, it's quite easy. If you want to change/recreate the Gremlin DB in order to add/suppr/change some question, answers you can change the request list in ai-sustainability\ai_sustainability\datas\script.json.  
And if you want to add some possible AI, you need to modify the Weight_matrix.xlsx (add a column and fill each ligne to add a AI, or add a ligne for a new question and put the coeficient for each AI) and don't forget to use the create_script_with_weight function in ai-sustainability\ai_sustainability\package_data_access\db_gestion.py.  
If you want to change element for the checklist, you will need to change they in the database_check_list located database located in ai-sustainability\ai_quality_check\package_data_access.  
<br><br>
Project made by Hennecart Alexandre and Filee Arnauld