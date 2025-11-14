"""
X - Documents per second
Y - Pages per document
"""
def compute_api_rates(X, Y):
    P = X * Y  # Pages per second
    N = 5 # Number of medications per page
    """
    1 Page with N medications LLM & third party calls details:
    OCR - 1
    ExtractText (Pro LLM) - 1
    Classify (Flash LLM) - 1
    Extractmedication (FLash LLM) - 1
    SemanticSearch - N
    Medispan Matching (Pro LLM) - N
    Normalize (Flash) - N
    
    LLM1 - OCR
    LLM2 - Flash
    LLM3 - Pro
    """
    api_rates = {
        'LLM1_rate': P*1, # 
        'LLM2_rate': P * 1 + P * 1 + P * N,
        'LLM3_rate': P * 1 + P * N,
        'Semantic_Search_rate': P * N,
        'Firestore_rate': P * 20,
        'Save_PDF_rate': X,
        'Split_Pages_rate': X
    }
    return api_rates
 
def compute_processing_time(parallelism=True):
    # Latencies (in seconds)
    T_LLM1 = 4
    T_LLM2 = 2
    T_LLM3 = 2
    T_Semantic_Search = 0.5
    T_Firestore = 0.1
 
    if parallelism:
        T_LLM2_total = T_LLM2  # Parallel LLM2 calls
        T_LLM3_total = T_LLM3  # Parallel LLM3 calls
        T_Firestore_total = T_Firestore  # Parallel Firestore calls
    else:
        T_LLM2_total = T_LLM2 * 4
        T_LLM3_total = T_LLM3 * 2
        T_Firestore_total = T_Firestore * 20
 
    T_page = T_LLM1 + T_LLM2_total + T_LLM3_total + T_Semantic_Search + T_Firestore_total
    return T_page
 
# Example usage:
X = 10  # Documents per second
Y = 5   # Pages per document
Z = 7   # Target processing time per document in seconds
 
api_rates = compute_api_rates(X, Y)
T_page = compute_processing_time(parallelism=True)
T_document = T_page  # Assuming negligible time for save and split
 
print("Required API Call Rates:")
for api, rate in api_rates.items():
    print(f"{api}: {rate} calls/sec")
 
print(f"\nProcessing Time per Document: {T_document:.2f} seconds")
print(f"Target Processing Time per Document (Z): {Z} seconds")
if T_document <= Z:
    print("Processing time meets the target.")
else:
    print("Processing time exceeds the target. Optimization needed.")