from fastapi import FastAPI, BackgroundTasks

app = FastAPI()


def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notifications for {email}: {message}"
        email_file.write(content)


@app.post("/send-notifications")
async def send_notification(email: str, background_task: BackgroundTasks):
    background_task.add_task(write_notification, email, message="I am sending you an email rn")
    return {"message": "Email sent successfully"}
