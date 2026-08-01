import argparse
import sys

from src.collection.collector import Collector
from src.cleaning.cleaner import Cleaner
from src.normalization.normalizer import Normalizer
from src.chunking.chunker import Chunker
from src.metadata.metadata_enricher import MetadataEnricher
from src.embedding.embedder import Embedder
from src.vectordb.db_loader import DBLoader
from src.retrieval.qa_engine import QAEngine

def run_all():
    print("Running Full Pipeline...")
    output_1 = Collector().execute(None)
    output_2 = Cleaner().execute(output_1)
    output_3 = Normalizer().execute(output_2)
    output_4 = Chunker().execute(output_3)
    output_5 = MetadataEnricher().execute(output_4)
    output_6 = Embedder().execute(output_5)
    output_7 = DBLoader().execute(output_6)
    print("Full Pipeline Finished!")

def main():
    parser = argparse.ArgumentParser(description="LLM Data Pipeline Runner")
    parser.add_argument("step", choices=[
        "collection", "cleaning", "normalization", 
        "chunking", "metadata", "embedding", 
        "vectordb", "retrieval", "all"
    ], help="Step to run in the pipeline")

    args = parser.parse_args()

    if args.step == "collection":
        Collector().execute(None)
    elif args.step == "cleaning":
        Cleaner().execute(None) # In real app, pass the correct input path
    elif args.step == "normalization":
        Normalizer().execute(None)
    elif args.step == "chunking":
        Chunker().execute(None)
    elif args.step == "metadata":
        MetadataEnricher().execute(None)
    elif args.step == "embedding":
        Embedder().execute(None)
    elif args.step == "vectordb":
        DBLoader().execute(None)
    elif args.step == "retrieval":
        QAEngine().execute(None)
    elif args.step == "all":
        run_all()

if __name__ == "__main__":
    main()
