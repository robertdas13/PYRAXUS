import React from 'react';
import { socialLinks } from '../mock';
import * as Icons from 'lucide-react';

const Footer = () => {
  const getIcon = (iconName) => {
    const IconComponent = Icons[iconName];
    return IconComponent ? <IconComponent size={20} /> : null;
  };

  return (
    <footer className="footer">
      <div className="footer-glow"></div>
      <div className="footer-content">
        <div className="footer-brand">
          <h3 className="footer-logo">PYRAXUS</h3>
          <p className="footer-tagline">Designing the future, one pixel at a time</p>
        </div>

        <div className="footer-social">
          {socialLinks.map((link, index) => (
            <a
              key={index}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="social-link"
              aria-label={link.platform}
            >
              {getIcon(link.icon)}
            </a>
          ))}
        </div>

        <div className="footer-bottom">
          <p className="footer-copyright">
            © PYRAXUS – Designed & Developed by Robert Das
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
