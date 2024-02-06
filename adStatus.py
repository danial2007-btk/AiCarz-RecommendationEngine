import random

def dummy(carID):
    
    is_approved = random.choice([True, False])

    # Construct the response based on the random result
    response = {
        'Id': carID,
        'rejectedImages': [],
        'checkedDescription': "",
        'adStatus': 'Approved' if is_approved else 'Rejected'
    }

    return response

