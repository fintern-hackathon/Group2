import { PropsWithChildren, useState } from 'react';
import { StyleSheet, TouchableOpacity, View, Modal, Pressable, Dimensions } from 'react-native';

import { ThemedText } from '@/components/ThemedText';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';

const windowWidth = Dimensions.get('window').width;

export function Collapsible({ children, title }: PropsWithChildren & { title: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const theme = useColorScheme() ?? 'light';

  // Badge'ın yatayda ortalanması için margin hesapla
  // (Varsayılan badge genişliği 250, windowWidth/2 - 125)
  const badgeLeft = Math.max(0, windowWidth / 2 - 125);

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.heading}
        onPress={() => setIsOpen(true)}
        activeOpacity={0.8}>
        <ThemedText style={styles.title}>{title}</ThemedText>
        <IconSymbol
          name="chevron.right"
          size={16}
          weight="medium"
          color={theme === 'light' ? Colors.light.icon : Colors.dark.icon}
          style={{ transform: [{ rotate: isOpen ? '90deg' : '0deg' }] }}
        />
      </TouchableOpacity>
      <Modal
        visible={isOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setIsOpen(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setIsOpen(false)}>
          <View style={[styles.modalContent, { left: badgeLeft }]}
            pointerEvents="box-none"
          >
            <View style={styles.heading}>
              <ThemedText style={styles.title}>{title}</ThemedText>
              <IconSymbol
                name="chevron.down"
                size={16}
                weight="medium"
                color={theme === 'light' ? Colors.light.icon : Colors.dark.icon}
              />
            </View>
            <View style={styles.contentInner}>{children}</View>
          </View>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'transparent',
    position: 'relative',
  },
  heading: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 8,
  },
  title: {
    fontSize: 17,
    fontWeight: '600',
    color: '#222',
    letterSpacing: 0.2,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.18)',
    justifyContent: 'flex-start',
    alignItems: 'center',
  },
  modalContent: {
    position: 'absolute',
    top: 110, // badge yüksekliği kadar aşağıda (gerekirse ayarlanabilir)
    width: 250,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#DEE2E6',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 8,
    zIndex: 9999,
  },
  contentInner: {
    backgroundColor: 'transparent',
    marginTop: 8,
  },
});
