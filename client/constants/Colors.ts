/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * There are many other ways to style your app. For example, [Nativewind](https://www.nativewind.dev/), [Tamagui](https://tamagui.dev/), [unistyles](https://reactnativeunistyles.vercel.app), etc.
 */

const tintColorLight = '#0057B8'; // Banking blue from Figma
const tintColorDark = '#fff';

export const Colors = {
  light: {
    text: '#0C0C0D', // Dark text from Figma
    background: '#fff',
    tint: tintColorLight,
    icon: '#687076',
    tabIconDefault: '#687076',
    tabIconSelected: tintColorLight,
    // Banking app specific colors
    primary: '#0057B8', // Main blue
    secondary: '#84BD00', // Green for progress
    gray: '#333333', // Dark gray
    lightGray: '#CCCCCC', // Light gray
    white: '#FFFFFF',
    black: '#000000',
    textSecondary: '#333333', // Secondary text color
    border: '#EDEDED', // Border color
    shadow: 'rgba(0, 0, 0, 0.12)', // Shadow color
  },
  dark: {
    text: '#ECEDEE',
    background: '#151718',
    tint: tintColorDark,
    icon: '#9BA1A6',
    tabIconDefault: '#9BA1A6',
    tabIconSelected: tintColorDark,
    // Banking app specific colors
    primary: '#0057B8',
    secondary: '#84BD00',
    gray: '#CCCCCC',
    lightGray: '#666666',
    white: '#FFFFFF',
    black: '#000000',
    textSecondary: '#CCCCCC',
    border: '#333333',
    shadow: 'rgba(0, 0, 0, 0.3)',
  },
};
