import React, { useState } from 'react';
import Header, { View } from './components/Header';
import BirthCardCalculator from './components/BirthCardCalculator';
import PrcLookup from './components/PrcLookup';
import LifePathCalculator from './components/LifePathCalculator';
import KarmaCardCalculator from './components/KarmaCardCalculator';
import CardLibrary from './components/CardLibrary';
import ArchetypeGuide from './components/ArchetypeGuide';
import DailyReading from './components/DailyReading';
import { Card } from './types';

const App: React.FC = () => {
  const [activeView, setActiveView] = useState<View>('BIRTH_CARD');
  
  const [birthDate, setBirthDate] = useState<{ month: number; day: number } | null>(null);
  const [birthCard, setBirthCard] = useState<Card | null>(null);
  const [personaCard, setPersonaCard] = useState<Card | null>(null);

  const handleStartOver = () => {
    setBirthDate(null);
    setBirthCard(null);
    setPersonaCard(null);
    setActiveView('BIRTH_CARD');
  }

  const handleBirthCardComplete = (date: { month: number; day: number }, card: Card) => {
    setBirthDate(date);
    setBirthCard(card);
    setPersonaCard(null); // Reset persona card if starting over
    setActiveView('PRC_LOOKUP');
  };

  const handlePersonaCardComplete = (card: Card) => {
    setPersonaCard(card);
    setActiveView('KARMA_CARDS');
  };

  const handleKarmaCardsComplete = () => {
    setActiveView('LIFE_PATH');
  }

  const renderContent = () => {
    switch (activeView) {
      case 'BIRTH_CARD':
        return <BirthCardCalculator onComplete={handleBirthCardComplete} />;
      case 'PRC_LOOKUP':
        return <PrcLookup birthDate={birthDate} birthCard={birthCard} onComplete={handlePersonaCardComplete} onStartOver={handleStartOver} />;
      case 'KARMA_CARDS':
        return <KarmaCardCalculator birthDate={birthDate} birthCard={birthCard} personaCard={personaCard} onComplete={handleKarmaCardsComplete} onStartOver={handleStartOver} />;
      case 'LIFE_PATH':
        return <LifePathCalculator birthDate={birthDate} birthCard={birthCard} personaCard={personaCard} onStartOver={handleStartOver} />;
      case 'DAILY_READING':
        return <DailyReading birthCard={birthCard} onStartOver={handleStartOver} />;
      case 'CARD_LIBRARY':
        return <CardLibrary />;
      case 'ARCHETYPES':
        return <ArchetypeGuide />;
      default:
        return <BirthCardCalculator onComplete={handleBirthCardComplete} />;
    }
  };

  return (
    <main className="min-h-screen w-full bg-gray-900 flex items-center justify-center p-4 selection:bg-purple-500 selection:text-white pt-32 sm:pt-28">
      <Header activeView={activeView} setActiveView={setActiveView} />
      {renderContent()}
    </main>
  );
};

export default App;