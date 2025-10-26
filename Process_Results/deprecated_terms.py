# This file is used to hold two keyword arrays to prevent cluttering the
# calculate_dataset_statistics.py and output_averaged_results.py file

initial_deprecated_search_terms = [
        # From JAXB
        "JAXBContext", "Marshaller", "Unmarshaller", "DatatypeConverter",
        # From JAX-WS
        "WebService", "SOAPBinding", "Service", "BindingProvider",
        # From JAF
        "DataHandler", "FileDataSource", "CommandMap", "MailcapCommandMap",
        # From CORBA
        "org.omg", "ORB", "Any", "PortableRemoteObject", "NamingContextExt",
        # From JavaTransaction API
        "UserTransaction", "TransactionManager", "XAResource",
        # Unsafe Thread/System cleanup APIs
        "Thread.stop(", "Thread.destroy(",
        "Runtime.runFinalizersOnExit(", "System.runFinalizersOnExit(",
        # From SecurityManager
        "checkAwtEventQueueAccess(", "checkMemberAccess(",
        "checkSystemClipboardAccess(", "checkTopLevelWindow(",
        # Policy class
        "javax.security.auth.Policy", "Policy.getPolicy", "Policy.setPolicy",
        # Deployment & tooling
        "javaws", "appletviewer", "javapackager",
        "wsimport", "wsgen", "xjc", "schemagen"
    ]

secondary_deprecated_search_terms = [
        # Removed in Java 11
        "javax.xml.bind.DatatypeConverter",
        "javax.xml.bind.JAXBContext",
        "javax.xml.bind.Marshaller",
        "javax.xml.bind.Unmarshaller",
        "javax.xml.ws.Service",
        "javax.xml.ws.Dispatch",
        "javax.xml.ws.BindingProvider",
        "javax.xml.ws.soap.SOAPBinding",
        "javax.jws.WebService",
        "javax.activation.FileDataSource",
        "javax.activation.DataHandler",
        "javax.activation.CommandMap",
        "javax.activation.MailcapCommandMap",
        "org.omg.CORBA.ORB",
        "org.omg.CORBA.Any",
        "org.omg.CosNaming.NamingContextExt",

        # Java EE / JTA types often present in Java 8 environments but not in Java 11 JDK
        "javax.transaction.UserTransaction",
        "javax.transaction.TransactionManager",

        # Policy in javax.security.auth (moved/absent by Java 11 JDK)
        "javax.security.auth.Policy",
        "javax.security.auth.Policy.getPolicy",
        "javax.security.auth.Policy.setPolicy",

        # Still exist but long-deprecated and unsafe
        "System.runFinalizersOnExit(",
        "Runtime.runFinalizersOnExit(",
        "Thread.stop(",
        ".stop(",
        "Thread.destroy(",
        ".destroy(",
        "SecurityManager.checkSystemClipboardAccess(",
        ".checkSystemClipboardAccess(",
        "SecurityManager.checkMemberAccess(",
        ".checkMemberAccess(",
        "SecurityManager.checkTopLevelWindow(",
        ".checkTopLevelWindow(",
        "SecurityManager.checkAwtEventQueueAccess(",
        ".checkAwtEventQueueAccess("
    ]