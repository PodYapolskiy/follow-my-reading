# from core.models import register_model
# import cv2
# from models_plugins.htr_pipeline import read_page, DetectorConfig, LineClusteringConfig, ReaderConfig, PrefixTree


# class SimpleHTRPlugin:
#     name = "simplehtr"
#     languages = ["eng"]
#     description = "SimpleHTR uses modern machine learning algorithms, which allows you to achieve fast and accurate text recognition."

#     def __init__(self):
#         with open("models_plugins/forHTR/words_alpha.txt") as f:
#             self.word_list = [w.strip().upper() for w in f.readlines()]
#         self.prefix_tree = PrefixTree(self.word_list)

#     def process_image(self, filename: str) -> str:
#         decoder = "word_beam_search"
#         img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
#         height = img.shape[0]
#         enlarge = 0
#         read_lines = read_page(
#             img,
#             detector_config=DetectorConfig(height=height, enlarge=enlarge),
#             line_clustering_config=LineClusteringConfig(min_words_per_line=2),
#             reader_config=ReaderConfig(decoder=decoder, prefix_tree=self.prefix_tree),
#         )
#         res = ""
#         for read_line in read_lines:
#             res += " ".join(read_word.text for read_word in read_line)
#         return res
