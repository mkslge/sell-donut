"use client";

import { useEffect } from "react";

import { fetchBackendJson } from "@/lib/api";


export function VisitLogger() {
  useEffect(() => {
    void fetchBackendJson("/logging/visit", {
      method: "POST",
    }).catch(() => {
      // Visit logging is best-effort and should never block rendering.
    });
  }, []);

  return null;
}
