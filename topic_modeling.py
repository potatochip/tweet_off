from gensim import corpora, models, similarities
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
import re
from collections import defaultdict


def remove_punctuation(text):
    return re.sub(ur"\p{P}+", "", text)


class Topics(object):
    def __init__(self, documents, num_topics=None, parts_of_speech=None, chunks=None):
        '''
        will only return a maximum number of topics equal to the number of documents.
        if a single document then will return a maximum number of topics equal to the number of sentences in that document.
        parts_of_speech expects a list of nltk pos and will exclude any word that does not fall on that list.
        chunks is the number of chunks to split very large documents into. if your documents are the size of novels then 500-1000 words is a good size.
        '''
        self.documents = documents
        self.num_topics = len(documents) if not num_topics else num_topics
        self.pos = parts_of_speech
        self.chunks = chunks
        self._process_text()
        self._get_topics()
        self._strip_topics()

    def _process_text(self):
        stop = stopwords.words('english')
        if len(self.documents) == 1:
            # only a single document passed so just modeling the topics of all the sentences in the document. useful if all of the documents being looked at are all about the same topic.
            docs = sent_tokenize(self.documents[0])
        else:
            docs = self.documents

        texts = []
        for doc in docs:
            words = word_tokenize(doc.lower())
            if self.pos:
                tagged = pos_tag(words)
                stripped = [tags[0] for tags in tagged if any(tags[1].startswith(p) for p in self.pos) and tags[0] not in stop]
            else:
                stripped = [word for word in words if word not in stop and len(word) > 1]
                # len(word) > 1 just an easy way of stripping out punctuation. any real words that length shouldnt be topics anyway.
            texts.append(stripped)

        # remove words that appear only once
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1
        self.texts = [[token for token in text if frequency[token] > 1] for text in texts]

    def _get_topics(self):
        dictionary = corpora.Dictionary(self.texts)
        corpus = [dictionary.doc2bow(text) for text in self.texts]
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]

        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=self.num_topics)
        self.topics = lsi.show_topics()
        self.corpus_lsi = lsi[corpus_tfidf]

    def _strip_topics(self):
        clean_topics = []
        for topic in self.topics:
            cleaned = re.findall(r'"(.*?)"', topic)
            clean_topics.append(cleaned)
        self.topics = clean_topics

    def topics_for_document(self, doc_num):
        '''doc_num is the index number for the document originally passed in documents.
        returns the cluster of topics that most represent the particular document.'''
        topic_scores = list(self.corpus_lsi)[doc_num]
        sorted_clusters = sorted(topic_scores, key=lambda x: x[1], reverse=True)
        most_relevant_cluster = sorted_clusters[0]
        return self.topics[most_relevant_cluster[0]]
