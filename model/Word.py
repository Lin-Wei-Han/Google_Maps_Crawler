from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

class Word:
    def __init__(self, ws_driver,pos_driver):
        self.ws_driver = ws_driver
        self.pos_driver = pos_driver
    
    def getNotsaveData(self, savedata):
        notsaveword = pd.read_excel('./lexicon/notsave.xlsx')
        notsaveword['notsave_word'] = notsaveword['notsave_word'].str.replace('\n', '')
        notsaveword = list(notsaveword['notsave_word'])

        notsavedata = savedata[~savedata['words'].isin(notsaveword)]
        return notsavedata.loc[:,['words','tfidf','pos','freq']]
    
    def getSaveData(self, notsavedata):
        saveword = pd.read_excel('./lexicon/save.xlsx')
        saveword['save_word'] = saveword['save_word'].str.replace('\n', '')
        saveword = list(saveword['save_word'])

        savedata = notsavedata[notsavedata['words'].isin(saveword)]
        return savedata.loc[:,['words','tfidf','pos','freq']]
    
    def selectionTag(self, selectdata,not_selectdata):
        notsavedata = self.getNotsaveData(selectdata)
        savedata = self.getSaveData(not_selectdata)
        merge_data = pd.concat([savedata, notsavedata], ignore_index=True)
        return merge_data
    
    def save(self,spot_data):
        target = ['Na','Nb','Nc']
        dataset_select = spot_data.loc[spot_data['pos'].isin(target)]
        dataset_not_select = spot_data.loc[~spot_data['pos'].isin(target)]
        dataset = self.selectionTag(dataset_select,dataset_not_select)
        dataset = dataset.sort_values(by="tfidf",ascending=False)
        return dataset
    
    def text_clean(self,content):
        # Run pipeline
        ws = self.ws_driver(content)
        pos = self.pos_driver(ws)

        # Convert results to strings
        ws_result = [','.join(['\'' + item + '\'' for item in sublist])for sublist in ws]
        pos_result = [','.join(['\'' + item + '\'' for item in sublist])for sublist in pos]

        # Perform TF-IDF calculation
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(ws_result)
        vocabulary = vectorizer.get_feature_names_out()
        total_tfidf_scores = {}
        for i in range(len(vocabulary)):
            word = vocabulary[i]
            total_tfidf_score = tfidf_matrix[:, i].sum()
            total_tfidf_scores[word] = total_tfidf_score

        sorted_tfidf_scores = sorted(
            total_tfidf_scores.items(), key=lambda x: x[1], reverse=True)

        top_k_words = [word for word, score in sorted_tfidf_scores]
        top_k_scores = [score for word, score in sorted_tfidf_scores]

        # Perform POS tagging on top words
        pos_tags = self.pos_driver(top_k_words)
        pos_final = [sublist[0] for sublist in pos_tags]

        # Calculate word frequency
        count_dict = {}
        for word in top_k_words:
            count = 0
            for sentence in ws_result:
                count += sentence.count(word)
            count_dict[word] = count

        # Create frequency DataFrame
        freq = pd.DataFrame({'words': list(count_dict.keys()),
                            'freq': list(count_dict.values())})

        # Create the final DataFrame
        df_final = pd.DataFrame(
            {'words': top_k_words, 'tfidf': top_k_scores, 'pos': pos_final})

        # Merge with frequency DataFrame
        merged_df = pd.merge(df_final, freq, on='words')

        return merged_df