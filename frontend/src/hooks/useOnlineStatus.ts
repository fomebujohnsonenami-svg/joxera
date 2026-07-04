import { useEffect, useState } from "react";

export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    function handleOnline() {
      setIsOnline(true);
      setWasOffline(true);
    }

    function handleOffline() {
      setIsOnline(false);
      setWasOffline(false);
    }

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  useEffect(() => {
    if (!wasOffline || !isOnline) return;
    const timer = setTimeout(() => setWasOffline(false), 4000);
    return () => clearTimeout(timer);
  }, [wasOffline, isOnline]);

  return { isOnline, wasOffline };
}
