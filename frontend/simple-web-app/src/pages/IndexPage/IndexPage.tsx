import {
  useInitData,
  useLaunchParams,
  useMainButton,
  useMiniApp,
} from "@telegram-apps/sdk-react";
import { Button, LargeTitle } from "@telegram-apps/telegram-ui";
import { useEffect } from "react";

export const IndexPage: React.FC = () => {
  const miniApp = useMiniApp();
  const mainButton = useMainButton();
  const initData = useInitData();
  const initDataRaw = useLaunchParams().initDataRaw;

  const greetBot = async () => {
    try {
      const formData = new URLSearchParams();
      formData.append("_auth", initDataRaw || "");

      const response = await fetch("/simple-web-app/greet", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "ngrok-skip-browser-warning": "69420",
        },
        body: formData,
      });

      if (response.status === 401) {
        alert("Unauthorized");
      }

      if (response.ok) {
        alert("Greeting sent");
      } else {
        alert("Error sending greeting");
      }
    } catch (error) {
      console.error("Error greeting:", error);
      alert("An error occurred. Please try again.");
    }
  };

  useEffect(() => {
    if (!initData) {
      mainButton.enable();
      mainButton.setText("Send info to bot");
      mainButton.show();
    }
  }, [miniApp, initData, mainButton]);

  mainButton.on("click", () => {
    miniApp.sendData("Some data");
  });

  return (
    <div className="flex h-screen w-full items-center justify-center bg-theme-bg-color">
      <div className="text-center">
        <LargeTitle weight="1" className="animate-fade-in">
          {initData ? (
            <>
              {`Hello, ${initData.user?.firstName}!`}
              <br />
              Web app has been launched from inline button!
            </>
          ) : (
            <>
              Hello!
              <br />
              Web app has been launched from reply button!
            </>
          )}
        </LargeTitle>
        {initData ? (
          <Button className="mt-2" onClick={greetBot}>
            Greet the bot!
          </Button>
        ) : null}
      </div>
    </div>
  );
};
