def test_sort_documents():
    from google.cloud import firestore
    # [START fs_order_by_name]
    # Create a reference to the collection
    start_at = {"created_at": "2024-01-01T00:00:00Z"}
    db = firestore.Client()
    # docs = db.collection(u'paperglass_documents') \
    #     .order_by('created_at', direction=firestore.Query.DESCENDING) \
    #     .where("file_name",">=","MEDICATION") \
    #     .where("file_name","<",'MEDICATION\uf8ff').where("patient_id","==","25e87397feea4c88bfdb2be61c61551a") \
    #     .where('active','==',True) \
    #     .start_at({"created_at": start_at}).limit(10) \
    #     .get()
    docs = db.collection(u'paperglass_documents') \
        .where("patient_id","==","25e87397feea4c88bfdb2be61c61551a") \
        .where("file_name",">=","MEDICATION") \
        .where("file_name","<",'MEDICATION\uf8ff') \
        .where('active','==',True) \
        .get()
    # [END fs_order_by_name]
    import pdb;pdb.set_trace()
    return docs