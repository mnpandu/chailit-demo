# vector_plot.py
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

def plot_similarity_results(docs_and_scores, embedding_model):
    texts = [doc.page_content for doc, _ in docs_and_scores]
    embeddings = embedding_model.embed_documents(texts)

    # Reduce to 2D
    reduced = PCA(n_components=2).fit_transform(embeddings)
    scores = [score for _, score in docs_and_scores]

    # Plot
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=scores, cmap='viridis', s=100)

    for i, text in enumerate(texts):
        snippet = text[:40].replace('\n', ' ') + "..."
        plt.text(reduced[i, 0]+0.01, reduced[i, 1]+0.01, snippet, fontsize=8)

    plt.title("2D Vector Space of Similar Documents")
    plt.xlabel("PCA Dimension 1")
    plt.ylabel("PCA Dimension 2")
    plt.grid(True)
    cbar = plt.colorbar(scatter)
    cbar.set_label("Similarity Score")
    plt.tight_layout()
    plt.show()

    # Also return reduced coordinates and scores for programmatic comparison
    return list(zip(texts, reduced.tolist(), scores))