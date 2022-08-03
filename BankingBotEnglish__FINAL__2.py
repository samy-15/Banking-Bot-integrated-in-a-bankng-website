import json
import boto3

def Check(accountNum): #Checks if an account actually exists in the database
    client = boto3.resource("dynamodb")
    table = client.Table("customerdetails")
    response = table.get_item(
    Key={
        'accountnumber': accountNum
    }
    )
    if 'Item' in response:
        return True #Returns True if Account Number exists
    else:
        return False #Returns False if Account Number does not exist

def AcBalSav(accountNum): #Returns savings account balance of a user
    client = boto3.resource("dynamodb")
    table = client.Table("customerdetails")
    response = table.get_item(
    Key={
        'accountnumber': accountNum
    }
    )
    sav = response['Item']['savings']
    sav = str(sav)
    return sav #Returns balance in savings account
   
        
    
def AcBalCur(accountNum): #Returns current account balance of a user
    client = boto3.resource("dynamodb")
    table = client.Table("customerdetails")
    response = table.get_item(
    Key={
        'accountnumber': accountNum
    }
    )
    cur = response['Item']['current']
    cur = str(cur)
    return cur #Returns balance in current account
    
def AcName(accountNum): #Returns name of Account Holder
    client = boto3.resource("dynamodb")
    table = client.Table("customerdetails")
    response = table.get_item(
    Key={
        'accountnumber': accountNum
    }
    )
    item = response['Item']['name']
    item2 = str(item)
    return item2
def debitSav(accountNum,amount): #Checks if adequate fund is available in savings for transfer
    client = boto3.resource("dynamodb")
    table = client.Table("customerdetails")
    response = table.get_item(
    Key={
        'accountnumber': accountNum
    }
    )
    sav = response['Item']['savings']
    sav = int(sav)
    if(sav>=amount):
        newSav = (sav - amount)
        response = table.update_item(
        Key = {
            'accountnumber': accountNum
        },
        UpdateExpression="SET savings= :s",
        ExpressionAttributeValues={
            ':s': newSav
        },
        ReturnValues="UPDATED_NEW" #Updates balance in savings after fund transfer
        )
        return True
    else:
        return False
def debitCur(accountNum,amount): #Checks if adequate fund is available in current for transfer
    client = boto3.resource("dynamodb")
    table = client.Table("customerdetails")
    response = table.get_item(
    Key={
        'accountnumber': accountNum
    }
    )
    cur = response['Item']['current']
    cur = int(cur)
    if(cur>=amount):
        newCur = (cur - amount)
        response = table.update_item(
        Key = {
            'accountnumber': accountNum
        },
        UpdateExpression="SET current= :c",
        ExpressionAttributeValues={
            ':c': newCur
        },
        ReturnValues="UPDATED_NEW"
        )
        return True
    else:
        return False
   
def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']
    
def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None    

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}

def elicit_intent(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [ message ] if message != None else None,
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }

def CheckBalance(intent_request): #Intent to check balance
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    account = str(get_slot(intent_request, 'accountType'))
    accountNum = str(get_slot(intent_request, 'accountNum'))
    if(Check(accountNum)):
        if(account=='savings' or account=='Savings'):
            balance = AcBalSav(accountNum)
        elif(account=='current' or account=='Current'):
            balance = AcBalCur(accountNum)
        accountName = str(AcName(accountNum))
        text = "Hello "+accountName+ " the balance on your "+account+" account is $"+balance
    else:
        text = "Sorry but the account number your entered is not registered with our bank"
    message =  {
            'contentType': 'PlainText',
            'content': text
        }
    fulfillment_state = "Fulfilled"    
    return close(intent_request, session_attributes, fulfillment_state, message)   

def Loans(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    loan = str(get_slot(intent_request, 'loanType'))
    if(loan=="Home"):
        text = "Interest on Home Loan is 6.5% "
    elif(loan=="Car"):
        text = "Interest on Car Loan is 7% "
    elif(loan=="Educational"):
        text = "Interest on Educational Loan is 5% "
    elif(loan=="Personal"):
        text = "Interest on Personal Loan is 9% "
    message =  {
            'contentType': 'PlainText',
            'content': text
        }
    fulfillment_state = "Fulfilled"    
    return close(intent_request, session_attributes, fulfillment_state, message)
    
def TransferFunds(intent_request): #Intent to transfer funds
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    accountNum = str(get_slot(intent_request, 'accountNum'))
    sourceAC = str(get_slot(intent_request, 'sourceAC'))
    amount = int(get_slot(intent_request, 'amount'))
    targetAC = str(get_slot(intent_request, 'targetAC'))
    name = str(get_slot(intent_request, 'name'))
    targetACNum = str(get_slot(intent_request, 'targetACNum'))
    bankName = str(get_slot(intent_request, 'bankName'))
    branch = str(get_slot(intent_request, 'branch'))
    if(sourceAC=='Savings' or sourceAC=='savings'):
        check = debitSav(accountNum,amount);
    elif(sourceAC=='Current' or sourceAC=='current'):
        check = debitCur(accountNum,amount);
    amount = str(amount)
    if(check):
        text = "$"+amount+" has been successfully transfered to the "+targetAC+" account of "+name
    else:
        text = "Sorry you are having insufficient balance in your "+sourceAC+" account"
    message =  {
            'contentType': 'PlainText',
            'content': text
        }
    fulfillment_state = "Fulfilled"    
    return close(intent_request, session_attributes, fulfillment_state, message)
    
    
def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    response = None
    # Dispatch to your bot's intent handlers
    if intent_name == 'CheckBalance':
        return CheckBalance(intent_request)
    elif intent_name == 'Loans':
        return Loans(intent_request)
    elif intent_name == 'TransferFunds':
        return TransferFunds(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    response = dispatch(event)
    return response