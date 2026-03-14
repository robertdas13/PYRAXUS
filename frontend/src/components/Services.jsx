import React from 'react';
import { services } from '../mock';
import { Card } from './ui/card';
import * as Icons from 'lucide-react';

const Services = () => {
  const getIcon = (iconName) => {
    const IconComponent = Icons[iconName];
    return IconComponent ? <IconComponent size={32} /> : null;
  };

  return (
    <section id="services" className="section-container section-dark">
      <div className="section-content">
        <div className="section-header">
          <h2 className="section-title">Services</h2>
          <div className="title-underline"></div>
          <p className="section-description">
            What I can do for you
          </p>
        </div>

        <div className="services-grid">
          {services.map((service) => (
            <Card key={service.id} className="service-card">
              <div className="service-icon">{getIcon(service.icon)}</div>
              <h3 className="service-title">{service.title}</h3>
              <p className="service-description">{service.description}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;