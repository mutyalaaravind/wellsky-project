import { useEffect } from "react";

type Props = {
  interval: number;
  callback: (...args: any[]) => any | Promise<any>;
};

const useAsyncTimeInterval = ({ interval = 10000, callback }: Props) => {
  useEffect(() => {
    const timerLoop: {
      isActive: boolean;
      timeToWait: number;
      timeOutId?: NodeJS.Timeout;
      startInterval: () => () => void;
      intervalLoop: () => void;
      clearTimer: () => void;
    } = {
      isActive: true,
      timeToWait: interval,
      timeOutId: undefined,
      startInterval: () => {
        if (timerLoop.timeOutId) {
          clearTimeout(timerLoop.timeOutId);
        }
        timerLoop.isActive = true;
        timerLoop.intervalLoop();
        return timerLoop.clearTimer;
      },
      intervalLoop: () => {
        if (!timerLoop.isActive) {
          return;
        }
        timerLoop.timeOutId = setTimeout(async () => {
          await callback();
          timerLoop.intervalLoop();
        }, timerLoop.timeToWait);
      },
      clearTimer: () => {
        timerLoop.isActive = false;
        clearTimeout(timerLoop.timeOutId);
      },
    };

    return timerLoop.startInterval();
  }, [callback, interval]);
};

export default useAsyncTimeInterval;
