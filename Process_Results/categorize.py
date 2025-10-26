def categorize(term):
    categories = {
    "JAXB": ["javax.xml.bind"],
    "JAX-WS": ["javax.xml.ws", "javax.jws"],
    "Activation": ["javax.activation"],
    "CORBA": ["org.omg"],
    "Transactions": ["javax.transaction"],
    "Security Policy": ["javax.security.auth.Policy"],
    "SecurityManager checks": [
        "SecurityManager.checkSystemClipboardAccess", ".checkSystemClipboardAccess",
        "SecurityManager.checkMemberAccess", ".checkMemberAccess",
        "SecurityManager.checkTopLevelWindow", ".checkTopLevelWindow",
        "SecurityManager.checkAwtEventQueueAccess", ".checkAwtEventQueueAccess"
    ],
    "Thread APIs": [
        "Thread.stop(", ".stop(",
        "Thread.destroy(", ".destroy(",
        "System.runFinalizersOnExit(", "Runtime.runFinalizersOnExit("
    ]
}

    for cat, patterns in categories.items():
        if any(p in term for p in patterns):
            return cat
    return "Other"