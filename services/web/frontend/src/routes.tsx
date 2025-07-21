import { createBrowserRouter, createRoutesFromElements, Route } from "react-router-dom";
import App from "./App";
import { DashboardPage } from "./pages/DashboardPage";
import { LibrariesPage } from "./pages/LibrariesPage";
import { GamesPage } from "./pages/GamesPage";
import { GameDetailPage } from "./pages/GameDetailPage";
import { PlatformsPage } from "./pages/PlatformsPage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<App />}>
        <Route index element={<DashboardPage />} />
        <Route path="libraries" element={<LibrariesPage />} />
        <Route path="games" element={<GamesPage />} />
        <Route path="games/:gameId" element={<GameDetailPage />} />
        <Route path="platforms" element={<PlatformsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </>
  )
);