import { useThemeColor } from '@/hooks/useThemeColor';
import { Image } from 'expo-image';
import React from 'react';
import { StyleSheet, View } from 'react-native';
import { ThemedText } from './ThemedText';

interface ProfileHeaderProps {
  userName?: string;
  avatarUrl?: string;
  greeting?: string;
}

export function ProfileHeader({ 
  userName = 'Alican', 
  avatarUrl, 
  greeting = 'İyi günler' 
}: ProfileHeaderProps) {
  const textColor = useThemeColor({}, 'text');
  const borderColor = useThemeColor({}, 'border');

  return (
    <View style={styles.container}>
      <View style={styles.avatarContainer}>
        <View style={[styles.avatarBorder, { borderColor }]}>
          <Image
            source={avatarUrl ? { uri: avatarUrl } : require('@/assets/images/icon.png')}
            style={styles.avatar}
            contentFit="cover"
          />
        </View>
      </View>
      <View style={styles.textContainer}>
        <ThemedText style={[styles.greeting, { color: textColor }]}>
          {greeting}
        </ThemedText>
        <ThemedText style={[styles.userName, { color: textColor }]}>
          {userName}
        </ThemedText>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  avatarContainer: {
    width: 64,
    height: 64,
  },
  avatarBorder: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 1,
    overflow: 'hidden',
  },
  avatar: {
    width: '100%',
    height: '100%',
    borderRadius: 32,
  },
  textContainer: {
    flex: 1,
  },
  greeting: {
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 14,
  },
  userName: {
    fontSize: 14,
    fontWeight: '700',
    lineHeight: 18,
  },
}); 