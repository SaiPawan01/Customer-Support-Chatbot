import {AuthContext} from "./Context.jsx";

import PropTypes from "prop-types";

export default function AuthContextProvider({ children }) {
    const value = useMemo(() => ({
        user: null,
    }),[]);
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

AuthContextProvider.propTypes = {
    children: PropTypes.node.isRequired,
}