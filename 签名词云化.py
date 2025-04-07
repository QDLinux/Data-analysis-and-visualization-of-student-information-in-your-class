import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

mottos = df['人生格言'].dropna().astype(str)
text = " ".join(mottos)

# Segment Chinese text
# Add custom words if jieba splits them incorrectly (optional)
# jieba.add_word("特定词")
seg_list = jieba.cut(text, cut_all=False)
processed_text = " ".join(seg_list)

# Generate Word Cloud (ensure FONT_PATH is correct)
try:
    wordcloud = WordCloud(
        font_path=FONT_PATH, # Crucial for Chinese characters
        width=800,
        height=400,
        background_color='white',
        stopwords={' ', ',', '.', '，', '。', '的', '是', '了'} # Add common stop words
    ).generate(processed_text)

    # Display the Word Cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("人生格言词云")
    plt.show()

    # Save the image
    wordcloud.to_file("motto_wordcloud.png")
    print("Generated motto_wordcloud.png")

except RuntimeError as e:
     print(f"Error generating word cloud. Check if FONT_PATH is correct: {FONT_PATH}. Error: {e}")
except Exception as e:
     print(f"An error occurred during word cloud generation: {e}")
