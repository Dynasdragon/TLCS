import './Login.css';
import { HashRouter, Route } from "react-router-dom";

export const Login = () => {
    return (
        <div>
            <div class="title-group">
                <img class="logo" src="../assets/CroppedLogo.png" alt=""/>
                <h1 class='title'>Traffic Light Control System</h1>
            </div>

            <div class="login_container">
                <div class="login_card">
                    <h2 class="subtitle">Login</h2>
                    <input class="usertextBox" placeholder="Username"/>
                        <input type="password" class="usertextBox" placeholder="Password"/>
                            <p onclick="true" class="forgotText">Forgot Password?</p>
                            <button name="loginBtn" class="login_button">Login</button>
                        </div>
                </div>
            </div>
    )
}