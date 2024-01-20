import * as React from 'react';
import {styled, createTheme, ThemeProvider} from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import MuiDrawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import MuiAppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';

import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';

import Link from '@mui/material/Link';
import MenuIcon from '@mui/icons-material/Menu';
import SourceIcon from '@mui/icons-material/Source';
import MemoryIcon from '@mui/icons-material/Memory';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import GitHubIcon from '@mui/icons-material/GitHub';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import FindInPageIcon from '@mui/icons-material/FindInPage';

import ExampleMenu from './components/ExampleMenu';
import PythonEditor from "./components/PythonEditor";
import SVEditor from "./components/SVEditor";
import NetlistViewer from "./components/NetlistViewer";

import apiConfig from "./apiConfig.json";
import magiaExamples from "./examples/magiaExamples.json";

import {PyCodeContext} from "./Contexts";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListItemButton from "@mui/material/ListItemButton";

function Copyright(props) {
    return (
        <Typography variant="body2" color="text.secondary" align="center" {...props}>
            {'Copyright © '}
            <Link color="inherit" href="https://www.github.com/khwong-c">
                Kin Wong
            </Link>{' '}
            {new Date().getFullYear()}
            {'.'}
        </Typography>
    );
}

const drawerWidth = 240;

const AppBar = styled(MuiAppBar, {
    shouldForwardProp: (prop) => prop !== 'open',
})(({theme, open}) => ({
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
    }),
    ...(open && {
        marginLeft: drawerWidth,
        width: `calc(100% - ${drawerWidth}px)`,
        transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    }),
}));

const Drawer = styled(MuiDrawer, {shouldForwardProp: (prop) => prop !== 'open'})(
    ({theme, open}) => ({
        '& .MuiDrawer-paper': {
            position: 'relative',
            whiteSpace: 'nowrap',
            width: drawerWidth,
            transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
            }),
            boxSizing: 'border-box',
            ...(!open && {
                overflowX: 'hidden',
                transition: theme.transitions.create('width', {
                    easing: theme.transitions.easing.sharp,
                    duration: theme.transitions.duration.leavingScreen,
                }),
                width: theme.spacing(7),
                [theme.breakpoints.up('sm')]: {
                    width: theme.spacing(9),
                },
            }),
        },
    }),
);

// TODO remove, this demo shouldn't need to reset the theme.
const defaultTheme = createTheme();

export default function App() {
    const [open, setOpen] = React.useState(true);
    const toggleDrawer = () => {
        setOpen(!open);
    };

    // Code Storages
    const [pyCode, setPyCode] = React.useState(localStorage.getItem('pythonValue') || magiaExamples["Sub Module"]);
    const [svCode, setSvCode] = React.useState("");
    const [netlist, setNetlist] = React.useState({});
    const [netlistErr, setNetlistErr] = React.useState("");
    const [loading, setLoading] = React.useState(false);

    const [display, setDisplay] = React.useState({
        svCode: false,
        netlist: true,
    });


    React.useEffect(() => {
    }, [pyCode]);

    const topName = "Top";

    const elaborate = (code) => {
        setSvCode("Loading...")
        setNetlist({})
        setNetlistErr("")
        setLoading(true)

        fetch(
            apiConfig.url + "/magia2sv", {
                method: 'POST',
                body: JSON.stringify({code: code, top: topName}),
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.err) {
                    setSvCode(data.err || "Failed to elaborate")
                    setNetlistErr("Failed to Elaborate SV Code")
                    setDisplay({
                        svCode: true,
                        netlist: false,
                    })
                    setLoading(false)
                } else {
                    setSvCode(data.sv_code)
                    synthesis(data.sv_code)
                }
            })
            .catch(error => {
                setSvCode("Failed to compile")
                setNetlistErr("Failed to Elaborate SV Code")
                setLoading(false)
            })
    }
    const synthesis = (code) => {
        fetch(
            apiConfig.url + "/yosys", {
                method: 'POST',
                body: JSON.stringify({code: code, top: topName}),
            })
            .then(resp => resp.json())
            .then(netlist => genSvg(netlist))
            .catch(error => {
                setNetlistErr("Failed to Synthesis Netlist.")
                setLoading(false)
            })
    }
    const genSvg = (yosysResult) => {
        fetch(
            apiConfig.url + "/yosys2svg", {
                method: 'POST',
                body: JSON.stringify(yosysResult),
            })
            .then(resp => resp.json())
            .then(data => {
                setNetlist(data)
                setLoading(false)
            })
            .catch(error => {
                setNetlistErr("Failed to Generate Netlist Image.")
                setLoading(false)
                console.log(error)
            })
    }

    return (
        <ThemeProvider theme={defaultTheme}>
            <PyCodeContext.Provider value={{
                code: pyCode, setCode: setPyCode
            }}>
                <Box sx={{display: 'flex'}}>
                    <CssBaseline/>
                    <AppBar position="absolute" open={open}>
                        <Toolbar
                            sx={{
                                pr: '24px', // keep right padding when drawer closed
                            }}
                        >
                            <IconButton
                                edge="start"
                                color="inherit"
                                aria-label="open drawer"
                                onClick={toggleDrawer}
                                sx={{
                                    marginRight: '36px',
                                    ...(open && {display: 'none'}),
                                }}
                            >
                                <MenuIcon/>
                            </IconButton>
                            <Typography
                                component="h1"
                                variant="h6"
                                color="inherit"
                                noWrap
                                sx={{flexGrow: 1}}
                            >
                                Magia Synthesis Playground
                            </Typography>
                            <IconButton
                                edge="start"
                                color="inherit"
                                sx={{
                                    marginRight: '36px',
                                }}
                                onClick={() => {
                                    setDisplay({
                                        svCode: true,
                                        netlist: false,
                                    })
                                }}
                            >
                                <SourceIcon sx={{
                                    marginRight: '8px',
                                    marginLeft: '8px',
                                }}/>
                                <Typography variant="h6" color="inherit" noWrap> SV Code View</Typography>
                            </IconButton>
                            <IconButton
                                edge="start"
                                color="inherit"
                                sx={{
                                    marginRight: '36px',
                                }}
                                onClick={() => {
                                    setDisplay({
                                        svCode: false,
                                        netlist: true,
                                    })
                                }}
                            >
                                <MemoryIcon sx={{
                                    marginRight: '8px',
                                    marginLeft: '8px',
                                }}/>
                                <Typography variant="h6" color="inherit" noWrap> Netlist View</Typography>
                            </IconButton>

                        </Toolbar>
                    </AppBar>
                    <Drawer variant="permanent" open={open}>
                        <Toolbar
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'flex-end',
                                px: [1],
                            }}
                        >
                            <IconButton onClick={toggleDrawer}>
                                <ChevronLeftIcon/>
                            </IconButton>
                        </Toolbar>

                        <Divider/>
                        <List component="nav">
                            <ListItemButton onClick={(e) => {
                                window.open("https://www.github.com/magia-hdl/magia")
                            }}>
                                <ListItemIcon>
                                    <GitHubIcon/>
                                </ListItemIcon>
                                <ListItemText primary="Project GitHub"/>
                            </ListItemButton>
                            <ListItemButton onClick={(e) => {
                                window.open("https://github.com/magia-hdl/magia/blob/main/docs/syntax.md")
                            }}>
                                <ListItemIcon>
                                    <MenuBookIcon/>
                                </ListItemIcon>
                                <ListItemText primary="Syntax Doc"/>
                            </ListItemButton>
                            <ListItemButton onClick={(e) => {
                                window.open("https://github.com/magia-hdl/magia-playground-syn")
                            }}>
                                <ListItemIcon>
                                    <FindInPageIcon/>
                                </ListItemIcon>
                                <ListItemText primary="Code of this App"/>
                            </ListItemButton>
                            <Divider/>
                            <ExampleMenu context={PyCodeContext}/>
                        </List>
                    </Drawer>
                    <Box
                        component="main"
                        sx={{
                            backgroundColor: (theme) =>
                                theme.palette.mode === 'light'
                                    ? theme.palette.grey[100]
                                    : theme.palette.grey[900],
                            flexGrow: 1,
                            height: '100vh',
                            overflow: 'auto',
                        }}
                    >
                        <Toolbar/>
                        <Container maxWidth="false" sx={{mt: 4, mb: 4}}>
                            <Grid container spacing={3}>
                                <PythonEditor
                                    context={PyCodeContext}
                                    onElaborate={(code) => {
                                        setSvCode(code);
                                        elaborate(code)
                                    }}
                                />
                                {
                                    display.svCode ? (
                                        <SVEditor value={svCode} loading={loading}/>
                                    ) : (
                                        <></>
                                    )
                                }
                                {
                                    display.netlist ? (
                                        <NetlistViewer netlist={netlist} err={netlistErr} top={topName}
                                                       loading={loading}/>
                                    ) : (
                                        <></>
                                    )
                                }
                            </Grid>
                            <Copyright sx={{pt: 4}}/>
                        </Container>
                    </Box>
                </Box>
            </PyCodeContext.Provider>
        </ThemeProvider>
    );
}
