from joblib import dump, load

actor_svm = load('Models/actor_svm.joblib')
objectives_svm = load('Models/objective_svm.joblib')
outputs_svm = load('Models/output_svm.joblib')
innovation_svm = load('Models/output_svm.joblib')

pred = actor_svm.predict("This project is about making sure that all people have houses.")
print(pred)