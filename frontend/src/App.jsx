import "./App.css";
import Navbar from "./components/Navbar";
import ChatbotPage from "./pages/ChatbotPage";
import ChatbotAssessPage from "./pages/ChatbotAssessPage";
import {
  createBrowserRouter,
  RouterProvider,
  Outlet,
} from "react-router-dom";

/**
 * Layout with Navbar
 */
function MainLayout() {
  return (
    <>
      <Navbar />
      <Outlet />
    </>
  );
}

const router = createBrowserRouter(
  [
    {
      path: "/",
      element: <MainLayout />,
      children: [
        {
          index: true,
          element: <ChatbotPage />,
        },
        {
          path: "chatbot",
          element: <ChatbotPage />,
        },
        {
          path: "chatbot/assess",
          element: <ChatbotAssessPage />,
        },
      ],
    },
  ],
  {
    basename: import.meta.env.BASE_URL,
  }
);

export default function App() {
  return <RouterProvider router={router} />;
}