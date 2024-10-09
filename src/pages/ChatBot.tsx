import { useEffect, useRef, useState } from "react";
import walleiaiImage from "../assets/images/fileasjhb 1.png";
import InputField from "../features/InputField";
import MoreSuggestions from "../features/MoreSuggestions";
import OfferView from "../features/OfferView";
import Suggestions from "../features/Suggestions";
import LetsConnect from "../features/LetsConnect";
import personIMage from "../assets/images/Ellipse 2.png";
import botImage from "../assets/images/Vector.png";
import ArrowDown from "../assets/icons/ArrowDown";
import SkeletonLoader from "../features/SkeletonLoader ";
import NewLetsConnect from "../features/NewLetsConnect";

type Props = {
  isDarkMode: boolean;
};

function ChatBot({ isDarkMode }: Props) {
  const [isRegistered, setIsRegistered] = useState<boolean>(false);
  const [messages, setMessages] = useState<{ text: string; sender: "user" | "bot" }[]>([]);
  const [showDownButton, setShowDownButton] = useState<boolean>(false);
  const [isTyping, setIsTyping] = useState<boolean>(false); // State to track bot typing

  useEffect(() => {
    const storedIsRegistered = localStorage.getItem("isRegistered");
    if (storedIsRegistered === "true") {
      setIsRegistered(true);
    }
  }, []);

  const handleSendMessage = (message: string) => {
    setMessages((prevMessages) => [...prevMessages, { text: message, sender: "user" }]);
    setIsTyping(true); // Show skeleton loader while waiting for the bot response

    // Simulate bot response after delay
    setTimeout(() => {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "Thank you for reaching out! We're currently under development. How can we assist you today?", sender: "bot" },
      ]);
      setIsTyping(false); // Remove skeleton loader when the bot responds
    }, 2000);
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleScroll = () => {
    const container = messagesContainerRef.current;
    if (container) {
      const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 100;
      setShowDownButton(!isAtBottom);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener("scroll", handleScroll);
    }

    return () => {
      if (container) {
        container.removeEventListener("scroll", handleScroll);
      }
    };
  }, []);
  return (
    <div className="grid grid-cols-12">
      <div className="col-span-3 h-[75vh] flex flex-col">
        <div className="flex items-center justify-center">
          {isRegistered && (
            <MoreSuggestions
              isDarkMode={isDarkMode}
              onSuggestionClick={handleSuggestionClick}
            />
          )}
        </div>
        <div className="flex mt-auto justify-start ms-8">
          {!isRegistered && <NewLetsConnect />}
        </div>
      </div>

      <div className="col-span-6 p-2 h-[73vh] w-[100%]">
        <div className="flex items-center justify-center">
          <div className={`relative ${isRegistered ? "-mt-7" : "-mt-3"}`}>
            <span
              className={`${isRegistered ? "text-4xl" : "text-5xl"
                } font-medium bg-clip-text text-transparent`}
              style={{
                backgroundImage: isDarkMode
                  ? "linear-gradient(92.92deg, #7BE53A 0.81%, #36AA00 99.19%)"
                  : "linear-gradient(92.92deg, #7BE53A 0.81%, #36AA00 99.19%)",
              }}
            >
              Hello, there
            </span>
            <br />
            <span
              className={`${isRegistered ? "text-4xl" : "text-5xl"
                } font-medium ${isDarkMode ? "text-gray-400" : "bg-clip-text text-transparent"}`}
              style={{
                backgroundImage: isDarkMode
                  ? "none"
                  : "linear-gradient(90.29deg, #CECECE 0.1%, #504F4F 99.9%)",
              }}
            >
              What can I help you with today?
            </span>
            <p className={`text-base ${isDarkMode ? "text-gray-400" : "text-[#BEBEBE]"} mt-1`}>
              Use one of the most common prompts below or use your own to begin
            </p>
            <div className="absolute bottom-[58%] right-2">
              <img
                src={walleiaiImage}
                alt="Wallei AI Bot"
                className={`h-auto ${isRegistered ? "w-28" : "w-36"}`}
              />
            </div>
          </div>
        </div>

        <div className={`flex h-[70%] ${isRegistered ? "flex-col" : "items-center"}`}>
          <div>
            {!isRegistered && <Suggestions isDarkMode={isDarkMode} />}
            {!isRegistered && <p className="text-[#BEBEBE] text-sm mt-4">More Suggestions</p>}
            <div
              className="mt-4 overflow-y-auto"
              style={{
                maxHeight: "58vh",
                scrollbarWidth: "none",
                msOverflowStyle: "none",
              }}
              ref={messagesContainerRef} // for scrolling
            >
              {messages.map((msg, index) => (
                <div key={index} className={`mb-4 text-sm flex items-center justify-end`}>
                  <div
                    className={`px-5 py-2 flex items-center rounded-lg 
                      ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                    style={{
                      maxWidth: "70%",
                      wordBreak: "break-word",
                      background: msg.sender === "user"
                        ? "linear-gradient(90.33deg, #DBFFCA 0.1%, #ABFF83 99.9%)"
                        : "linear-gradient(90.33deg, #E0E0E0 0.1%, white 99.9%)",
                      color: msg.sender === "user" ? "#4ABC15" : "black",
                    }}
                  >
                    {msg.text}
                  </div>
                  <img
                    src={msg.sender === "user" ? personIMage : botImage}
                    className={`ms-3 ${msg.sender === "user" ? "w-7" : "w-[1.375rem]"}`}
                    alt={msg.sender === "user" ? "User" : "Bot"}
                  />
                </div>
              ))}
              {isTyping && <SkeletonLoader />}
              <div ref={messagesEndRef} />
            </div>

            {showDownButton && (
              <div className="text-white p-2 rounded-full  animate-pulse
              cursor-pointer fixed bottom-[15%] left-[50%]" onClick={scrollToBottom}
              style={{background:"linear-gradient(90.33deg, #E0E0E0 0.1%, white 99.9%)"}}>
                <ArrowDown />
              </div>
            )}
          </div>
        </div>

        <div className="absolute text-center bottom-0.5 w-[50%]">
          <InputField
            isDarkMode={isDarkMode}
            isRegistered={isRegistered}
            setIsRegistered={setIsRegistered}
            onSendMessage={handleSendMessage}
          />
          <span className="text-xs text-[#999999]">
            Wallya may display inaccurate info, including about availability, so double-check its responses
          </span>
        </div>
      </div>

      <div className="col-span-3 flex items-end justify-end me-8 h-[75vh]">
        <OfferView />
      </div>
    </div>
  );
}

export default ChatBot;