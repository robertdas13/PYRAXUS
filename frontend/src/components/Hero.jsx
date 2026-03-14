import React from 'react';
import { ArrowRight, Download } from 'lucide-react';
import { Button } from './ui/button';

const Hero = () => {
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="home" className="hero-section">
      <div className="hero-grid-bg"></div>
      <div className="hero-gradient"></div>
      
      <div className="hero-content">
        <div className="hero-text">
          <h1 className="hero-title">
            CODE THE FUTURE
            <br />
            <span className="text-gradient">WITH PYRAXUS</span>
          </h1>
          <p className="hero-subtitle">UI/UX Designer & Frontend Developer</p>
          <p className="hero-description">
            I design and develop futuristic digital experiences that combine
            creativity, usability, and performance.
          </p>
          <div className="hero-buttons">
            <Button
              onClick={() => scrollToSection('projects')}
              className="btn-primary"
            >
              View Projects
              <ArrowRight className="ml-2" size={18} />
            </Button>
            <Button
              onClick={() => scrollToSection('contact')}
              variant="outline"
              className="btn-secondary"
            >
              Hire Me
              <Download className="ml-2" size={18} />
            </Button>
          </div>
        </div>

        <div className="hero-image-container">
          <div className="hero-glow"></div>
          <div className="hero-image">
            <img
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=faces"
              alt="Robert Das"
              className="profile-image"
            />
          </div>
        </div>
      </div>

      <div className="scroll-indicator">
        <div className="scroll-line"></div>
      </div>
    </section>
  );
};

export default Hero;