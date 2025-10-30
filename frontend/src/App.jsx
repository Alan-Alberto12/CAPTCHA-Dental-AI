import React from "react";
import SignUp from './pages/SignUp'
import Dashboard from "./pages/Dashboard"; // resolves to index.jsx in that folder
import PlayPage from "./pages/PlayPage.jsx";
import Header from "./components/Header.jsx";
import BottomTabs from "./components/BottomTab.jsx";

export default function App() {
  //return <Dashboard />;
  return (
    <>
        <Header/>
        <Dashboard/>
        <BottomTabs active="play"/>
    </>

  )
}
