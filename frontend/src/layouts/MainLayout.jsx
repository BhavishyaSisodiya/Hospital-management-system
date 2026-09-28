import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChatBot from "../components/ChatBot";

function MainLayout({ children }) {
  return (
    <div className="app-layout">
      <Navbar />

      <div className="layout-body">
        <Sidebar />

        <main className="main-content">
          {children}
        </main>
      </div>

      <ChatBot />
    </div>
  );
}

export default MainLayout;