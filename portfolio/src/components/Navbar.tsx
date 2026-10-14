import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, ShieldAlert } from 'lucide-react';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const links = ['Home', 'About', 'Pipeline', 'Technologies'];

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'py-4 glass border-b border-white/5' : 'py-6 bg-transparent'}`}>
      <div className="max-w-7xl mx-auto px-6 sm:px-12 flex items-center justify-between">
        <a href="#home" className="flex items-center gap-2 text-xl font-bold tracking-tight">
          <ShieldAlert className="text-primary" />
          <span>CarDD<span className="text-primary">.ai</span></span>
        </a>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          <ul className="flex items-center gap-6">
            {links.map((link) => (
              <li key={link}>
                <a href={`#${link.toLowerCase()}`} className="text-sm text-foreground/80 hover:text-white transition-colors font-medium">
                  {link}
                </a>
              </li>
            ))}
          </ul>
          <a href="http://127.0.0.1:5000" target="_blank" rel="noreferrer" className="px-5 py-2 rounded-full bg-primary hover:bg-primary/90 text-white text-sm font-semibold transition-colors shadow-lg shadow-primary/30">
            Open Dashboard
          </a>
        </nav>

        {/* Mobile Toggle */}
        <button className="md:hidden text-foreground" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          {mobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-full left-0 right-0 glass border-b border-white/10 md:hidden flex flex-col items-center py-6 gap-4"
          >
            {links.map((link) => (
              <a 
                key={link} 
                href={`#${link.toLowerCase()}`} 
                onClick={() => setMobileMenuOpen(false)}
                className="text-lg font-medium text-foreground/80 hover:text-white"
              >
                {link}
              </a>
            ))}
            <a href="http://127.0.0.1:5000" target="_blank" rel="noreferrer" className="px-6 py-3 rounded-full bg-primary text-white text-md font-semibold mt-2">
              Open Dashboard
            </a>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Navbar;
