import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import About from './components/About';
import Technologies from './components/Technologies';
import Pipeline from './components/Pipeline';
import Footer from './components/Footer';

function App() {
  return (
    <div className="bg-background min-h-screen text-foreground relative overflow-hidden">
      {/* Abstract Animated Background Glows */}
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/20 blur-[120px] pointer-events-none" />
      <div className="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-accent/20 blur-[120px] pointer-events-none" />
      
      <Navbar />
      
      <main className="relative z-10 max-w-7xl mx-auto px-6 sm:px-12">
        <Hero />
        <About />
        <Pipeline />
        <Technologies />
      </main>
      
      <Footer />
    </div>
  );
}

export default App;
