export enum Suit {
  Hearts = 'Hearts',
  Clubs = 'Clubs',
  Diamonds = 'Diamonds',
  Spades = 'Spades',
  Joker = 'Joker',
}

export enum Rank {
  Ace = 'A',
  Two = '2',
  Three = '3',
  Four = '4',
  Five = '5',
  Six = '6',
  Seven = '7',
  Eight = '8',
  Nine = '9',
  Ten = '10',
  Jack = 'J',
  Queen = 'Q',
  King = 'K',
  Joker = 'Joker',
}

export interface Card {
  suit: Suit;
  rank: Rank;
  value: number; // The solar value
  name: string; // e.g., "Ace of Hearts"
}

export interface CardArchetype {
  name: string;
  archetype: string;
  suit_realm: string;
  suit_focus: string;
  core_nature: string;
  personality: string;
  strengths: string;
  challenges: string;
  life_approach: string;
  in_domain_title: string;
  in_domain_description: string;
  shadow_keywords: string[];
}

export interface NumberMeaning {
  number: number;
  name: string;
  core_trait: string;
}

export interface SuitInfluence {
  suit: Suit;
  realm: string;
  focus: string;
  energy: string;
}

export interface ArchetypeSystemData {
  numberMeanings: NumberMeaning[];
  suitInfluences: SuitInfluence[];
  cards: {
    [key: string]: CardArchetype;
  };
}


export interface LifePathData {
  [birthCardName: string]: {
    Mercury: string;
    Venus: string;
    Mars: string;
    Jupiter: string;
    Saturn: string;
    Uranus: string;
    Neptune: string;
    Pluto: string;
    Result: string;
    'Cosmic Lesson': string;
    'Cosmic Moon': string;
    'Transformed Self': string;
  };
}

export interface StageDescription {
  short: string;
  full: string;
}

export interface RelationalMeaning {
  short: string;
  full: string;
}

export interface StageInfo {
  name: string;
  description: StageDescription;
  relational: RelationalMeaning;
}
