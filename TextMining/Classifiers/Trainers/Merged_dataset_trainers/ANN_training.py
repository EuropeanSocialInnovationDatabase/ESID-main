from ANN_Experiments import UniversalNNClassifier,read_files
import pandas as pd
from sklearn.utils import resample

if  __name__ == '__main__':
    path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded"
    # path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded2"
    # path = "../../../../Helpers/SI_dataset/Output/SI_withExcluded3"
    # path = "../../../../Helpers/SI_dataset/Output/SI_only_balanced"
    # path = "../../../../Helpers/SI_dataset/Output/SI_only"
    annotations = read_files(path)
    # annotations = load_database_description_dataset()
    # transfer_to_database(annotations)
    # exit(1)
    texts = []
    classA = []
    ### Working on Objectives
    print("Working on Objectives")

    for anns in annotations:
        texts.append(anns[1])
        value = anns[2]
        if value >= 2:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    # df_majority = df[df.classa == 1]
    # df_minority = df[df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=530,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # df = df_upsampled

    cls = UniversalNNClassifier()
    X_train = df['text']
    y_train = df['classa']

    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Objectives_NN")

    ### Actors
    print("Working on Actors")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[3]
        if value >= 2:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    # df_majority = df[df.classa == 1]
    # df_minority = df[df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=440,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # df = df_upsampled
    cls = UniversalNNClassifier()
    X_train = df['text']
    y_train = df['classa']

    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Actors_NN")

    ### Outputs
    print("Working on Outputs")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[4]
        if value >= 2:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    # df_majority = df[df.classa == 1]
    # df_minority = df[df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=510,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # df = df_upsampled
    cls = UniversalNNClassifier()
    X_train = df['text']
    y_train = df['classa']

    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Outputs_NN")

    ### Innovativeness
    print("Working on Innovativness")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[5]
        if value >= 2:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    # df_majority = df[df.classa == 1]
    # df_minority = df[df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=510,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # df = df_upsampled
    cls = UniversalNNClassifier()
    X_train = df['text']
    y_train = df['classa']

    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Innovativeness_NN")