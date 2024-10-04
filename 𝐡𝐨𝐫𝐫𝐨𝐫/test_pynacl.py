try:
    import nacl
    print("PyNaCl is installed correctly.")
except ImportError as e:
    print(f"Error importing PyNaCl: {e}")
 