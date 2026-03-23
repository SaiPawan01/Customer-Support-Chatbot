from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Document
from .utils.document_processing import load_pdf, chunk_text, generate_embeddings, store_embeddings
from .utils.document_processing import get_pinecone_instance


@receiver(post_save, sender=Document)
def start_document_pipeline(sender, instance, created, **kwargs):
    if created and instance.file:
        docs = load_pdf(instance)
        docs = chunk_text(docs=docs,instance=instance)
        embeddings = generate_embeddings(chunks=docs)
        store_embeddings(vectors=embeddings)

        instance.status = "completed"
        instance.save()




@receiver(post_delete, sender=Document)
def delete_document_embeddings(sender, instance, **kwargs):
    try:
        pc = get_pinecone_instance()
        index = pc.Index('documents')
        index.delete(filter={"doc_id":{"$eq" : instance.id}})
    except Exception as e:
        pass
