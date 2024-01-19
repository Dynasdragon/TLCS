import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Login } from './pages/Login'

const AllRoutes = () => {
    return (
        <Router>
            <Routes>
                <Route path='/' element={<Login></Login> }/>
            </Routes>
        </Router>
    )
}

export default AllRoutes;