from datetime import datetime



import storage

from models import PROCESSING, SENT, FAILED, RETRY_PENDING

from providers.email_provider import send as send_email

from providers.sms_provider import send as send_sms

from providers.push_provider import send as send_push





def _apply_provider_response(n, response):

    result = response["Result"]

    if result == "Success":

        n.status = SENT

        n.lastError = None

    elif result == "TemporaryFailure":

        n.status = RETRY_PENDING

        n.lastError = response["Message"]

    elif result in ("PermanentFailure", "InvalidRequest"):

        n.status = FAILED

        n.lastError = response["Message"]

    else:

        n.status = FAILED

        n.lastError = response.get("Message", "Unknown provider result")





class NotificationProcessor:

    def send_one(self, n):

        n.status = PROCESSING

        n.attempts += 1

        n.lastAttemptAt = datetime.now().isoformat()



        if not n.targetChannels:

            n.status = FAILED

            n.lastError = "No target channels"

            return

        target = n.targetChannels[0]



        if target["type"] == "email":

            response = send_email({"recipient": target["value"], "message": n.message})

        elif target["type"] == "sms":

            response = send_sms({"recipient": target["value"], "message": n.message})

        elif target["type"] == "push":

            response = send_push({"recipient": target["value"], "message": n.message})

        else:

            n.status = FAILED

            n.lastError = "Unknown channel"

            return



        _apply_provider_response(n, response)



    def send_all(self):

        pending = [n for n in storage.get_all() if n.status == PENDING]

        for n in pending:

            self.send_one(n)

