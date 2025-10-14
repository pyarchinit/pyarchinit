#!/usr/bin/env python3
"""
Utility per resettare le connessioni database singleton
Utile quando si cambia database o in caso di problemi di connessione
"""

def reset_all_connections():
    """Reset di tutte le connessioni singleton"""
    try:
        from .pyarchinit_db_manager import DbConnectionSingleton
        DbConnectionSingleton.clear_instances()
        print("✅ Tutte le connessioni singleton sono state resettate")
        return True
    except Exception as e:
        print(f"❌ Errore nel reset delle connessioni: {e}")
        return False

def get_active_connections():
    """Ottieni informazioni sulle connessioni attive"""
    try:
        from .pyarchinit_db_manager import DbConnectionSingleton
        instances = DbConnectionSingleton._instances
        
        if not instances:
            print("ℹ️  Nessuna connessione singleton attiva")
            return []
        
        active_connections = []
        for conn_str, instance in instances.items():
            # Nascondi la password dalla connection string
            safe_conn_str = conn_str
            if '@' in conn_str:
                parts = conn_str.split('@')
                if len(parts) > 1:
                    user_part = parts[0].split('://')[-1]
                    if ':' in user_part:
                        user, _ = user_part.split(':', 1)
                        safe_conn_str = conn_str.replace(user_part, f"{user}:***")
            
            active_connections.append({
                'connection_string': safe_conn_str,
                'engine_status': 'connected' if hasattr(instance, 'engine') and instance.engine else 'disconnected',
                'session_factory': 'available' if hasattr(instance, 'Session') and instance.Session else 'not_available'
            })
        
        print(f"🔗 {len(active_connections)} connessioni singleton attive:")
        for i, conn_info in enumerate(active_connections, 1):
            print(f"  {i}. {conn_info['connection_string']}")
            print(f"     Engine: {conn_info['engine_status']}")
            print(f"     Session: {conn_info['session_factory']}")
        
        return active_connections
        
    except Exception as e:
        print(f"❌ Errore nel recupero delle connessioni: {e}")
        return []

if __name__ == "__main__":
    print("🔧 PyArchInit Connection Reset Utility")
    print("=" * 40)
    
    # Mostra connessioni attive
    get_active_connections()
    
    # Chiedi se resettare
    response = input("\n❓ Vuoi resettare tutte le connessioni? (y/N): ")
    if response.lower() in ['y', 'yes', 's', 'si']:
        reset_all_connections()
        print("\n🔄 Riavvia QGIS per applicare completamente il reset")
    else:
        print("❌ Reset annullato")