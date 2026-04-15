/**
 * GlimmerAvatar — mood-aware animated persona display for the persona page.
 *
 * REQ:GlimmerPersonaPage
 * REQ:VisualPersonaSupport
 *
 * Displays a randomly-selected avatar image matching Glimmer's current mood.
 * Transitions with fade out/in when mood changes (e.g. to "thinking" when
 * processing a question, back to the ambient mood when done).
 *
 * Images: 400×~600px PNGs with transparent backgrounds, served from
 * /avatar-images/glimmer-avatar-{mood}-{nn}.png
 */

"use client";

import { useEffect, useState, useRef } from "react";

export type GlimmerMoodType = "bau" | "happy" | "grumpy" | "thinking" | "worried";

const MOOD_IMAGE_COUNTS: Record<GlimmerMoodType, number> = {
  bau: 9,       // 00-08
  grumpy: 3,    // 00-02
  happy: 3,     // 00-02
  thinking: 3,  // 00-02
  worried: 4,   // 00-03
};

function getRandomImageForMood(mood: GlimmerMoodType): string {
  const count = MOOD_IMAGE_COUNTS[mood];
  const index = Math.floor(Math.random() * count);
  const nn = index.toString().padStart(2, "0");
  return `/avatar-images/glimmer-avatar-${mood}-${nn}.png`;
}

interface GlimmerAvatarProps {
  mood: GlimmerMoodType;
  isThinking?: boolean;
  className?: string;
}

export function GlimmerAvatar({ mood, isThinking = false, className }: GlimmerAvatarProps) {
  const activeMood = isThinking ? "thinking" : mood;
  const [currentSrc, setCurrentSrc] = useState<string>("");
  const [animClass, setAnimClass] = useState("avatar-mood-enter");
  const prevMoodRef = useRef(activeMood);

  // Set initial image on mount
  useEffect(() => {
    setCurrentSrc(getRandomImageForMood(activeMood));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle mood transitions with fade out/in
  useEffect(() => {
    if (prevMoodRef.current === activeMood) return;
    prevMoodRef.current = activeMood;

    // Fade out
    setAnimClass("avatar-mood-exit");

    const timer = setTimeout(() => {
      // Switch image and fade in
      setCurrentSrc(getRandomImageForMood(activeMood));
      setAnimClass("avatar-mood-enter");
    }, 400); // matches the CSS transition duration

    return () => clearTimeout(timer);
  }, [activeMood]);

  if (!currentSrc) return null;

  return (
    <div
      className={`relative flex-shrink-0 ${className ?? ""}`}
      data-testid="glimmer-avatar"
      data-mood={activeMood}
    >
      {/* Subtle glow behind the avatar matching mood */}
      <div className="absolute inset-0 -m-4 rounded-full blur-2xl opacity-20 pointer-events-none"
        style={{
          background: activeMood === "happy"
            ? "radial-gradient(circle, rgba(52, 211, 153, 0.3), transparent)"
            : activeMood === "worried"
            ? "radial-gradient(circle, rgba(255, 183, 131, 0.3), transparent)"
            : activeMood === "grumpy"
            ? "radial-gradient(circle, rgba(255, 180, 171, 0.3), transparent)"
            : activeMood === "thinking"
            ? "radial-gradient(circle, rgba(129, 140, 248, 0.4), transparent)"
            : "radial-gradient(circle, rgba(129, 140, 248, 0.2), transparent)",
        }}
      />

      <img
        src={currentSrc}
        alt={`Glimmer — ${activeMood}`}
        className={`relative z-10 w-[200px] h-auto object-contain drop-shadow-[0_8px_32px_rgba(0,0,0,0.5)] ${animClass}`}
        data-testid="glimmer-avatar-img"
      />

      {/* Thinking indicator */}
      {isThinking && (
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 z-20 flex gap-1.5">
          <span className="h-2 w-2 rounded-full bg-primary animate-bounce [animation-delay:0ms]" />
          <span className="h-2 w-2 rounded-full bg-primary animate-bounce [animation-delay:150ms]" />
          <span className="h-2 w-2 rounded-full bg-primary animate-bounce [animation-delay:300ms]" />
        </div>
      )}
    </div>
  );
}

