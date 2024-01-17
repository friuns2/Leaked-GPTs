from typing import Optional, List, Mapping, Any
import traceback
from time import sleep
from typing import Dict, Callable
from langchain.llms.base import LLM
import requests
from .driver import ChatGptDriver


class GPT4OpenAI(LLM):
    history_data: Optional[List] = []
    token: Optional[str]
    chatbot: Optional[ChatGptDriver] = None
    call: int = 0
    conversation: Optional[str] = ""
    headless: bool = True
    __file__ = __file__
    model: str = "gpt-4"
    gpts: str = None

    #### WARNING : for each api call this library will create a new chat on chat.openai.com
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _create_chatbot(self):
        if self.chatbot is None:
            if self.token is None:
                raise ValueError(
                    "Need a token , check https://chat.openai.com/api/auth/session for get your token"
                )
            else:
                if self.conversation == "":
                    self.chatbot = ChatGptDriver(
                        self.token,
                        headless=self.headless,
                        model=self.model,
                        gpts_url=self.gpts,
                    )
                elif self.conversation != "":
                    self.chatbot = ChatGptDriver(
                        self.token,
                        headless=self.headless,
                        model=self.model,
                        conversation_id=self.conversation,
                        gpts_url=self.gpts,
                    )
                else:
                    raise ValueError("Something went wrong")

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if stop is not None:
            pass
            # raise ValueError("stop kwargs are not permitted.")
        # token is a must check
        self._create_chatbot()

        response = ""
        # OpenAI: 50 requests / hour for each account
        if self.call >= 45:
            raise ValueError(
                "You have reached the maximum number of requests per hour ! Help me to Improve. Abusing this tool is at your own risk"
            )
        else:
            sleep(2)
            try:
                data = self.chatbot.chat(prompt)
            except Exception as e:
                self.chatbot.driver.save_screenshot("error.png")
                sleep(1)
                self.chatbot.driver.save_screenshot("error2.png")
                print("Error:")
                print(e)
                print(traceback.print_exc())
                # sleep(300) # So user can debug the issue
                raise
            # print(data)
            response = data["message"]
            self.conversation = data["conversation_id"]
            FullResponse = data
            self.call += 1

        # add to history
        self.history_data.append({"prompt": prompt, "response": response})

        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model": self.model, "token": self.token}

    def generate_image(self, prompt: str, image_path: Optional[str] = None) -> bytes:
        """
        Generate an image from a prompt. If image_path is passed, the image will be saved to that path.

        Return:
            bytes: image bytes
        """
        self._create_chatbot()
        img_url = self.chatbot.generate_image(prompt)
        # Download an image to a local file path
        img_data = requests.get(img_url).content

        if image_path is not None:
            with open(image_path, "wb") as file:
                file.write(img_data)

        return img_data

    def close(self):
        """
        Close the Chrome browser
        """
        self.chatbot.driver.quit()
