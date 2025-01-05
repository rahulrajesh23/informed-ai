import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../types';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import PersonIcon from '@mui/icons-material/Person';
import SettingsIcon from '@mui/icons-material/Settings';
import { AppDispatch } from '../../store/store';

import HealthUpdate from '../../Containers/HealthUpdate/HealthUpdate';
import UserUpdate from '../../Containers/UserUpdate/UserUpdate';
import DialogWrapper from '../DialogWrapper/DialogWrapper';
import { useToastMessage } from '../../Containers/HOCLayout/ToastMessageContext';
import styles from './Header.module.css';
import * as userActions from '../../store/actionCreators/userActionCreators';
import UserSettings from '../../Containers/UserSettings/UserSettings';

interface MenuItem {
  code: 'profile' | 'health_details' | 'settings';
  label: string;
  dialog?: boolean;
  dialogProps: {
    title: string;
    success_msg: string;
  };
}

interface DialogFormState {
  profile: Record<string, any>;
  health_details: Record<string, any>;
  settings: Record<string, any>;
}

const menuItems: MenuItem[] = [
  {
    code: 'profile',
    label: 'Profile',
    dialog: true,
    dialogProps: {
      title: "User Details",
      success_msg: "User details updated successfully!",
    }
  },
  {
    code: 'health_details',
    label: 'Health Details',
    dialogProps: {
      title: "Health Details",
      success_msg: "User details updated successfully!",
    }
  },
  {
    code: 'settings',
    label: 'Settings',
    dialogProps: {
      title: "User Settings",
      success_msg: "Settings updated successfully!",
    }
  }
];

const initialDialogFormState: DialogFormState = {
  profile: {},
  health_details: {},
  settings: {}
};

export const Menu: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const user = useSelector((state: RootState) => state.user.user);
  const [open, setOpen] = useState(false);
  const [dialogFormState, setDialogFormState] = useState<DialogFormState>(initialDialogFormState);
  const [isDialogOpen, openDialog] = useState(false);
  const [selectedMenuItem, selectMenuItem] = useState<MenuItem['code'] | ''>('');
  const showToastMessage = useToastMessage();

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpen(newOpen);
  };

  const handleDialogClose = () => {
    selectMenuItem('');
    openDialog(false);
  };

  useEffect(() => {
    if(selectedMenuItem) {
      openDialog(true);
    }
  }, [selectedMenuItem]);

  useEffect(() => {
    return () => {
      setDialogFormState(initialDialogFormState);
    };
  }, []);

  const handleDialogFormChange = (updatedFormState: Record<string, any>) => {
    setDialogFormState(prev => ({
      ...prev,
      [selectedMenuItem]: { ...updatedFormState }
    }));
  };

  const handleOnSave = () => {
    if (!selectedMenuItem) return;

    switch(selectedMenuItem) {
      case "profile":
        dispatch(userActions.setUserDetails({ payload: dialogFormState[selectedMenuItem] }));
        break;
      case 'health_details':
        dispatch(userActions.setUserMedicalDetails({ payload: dialogFormState[selectedMenuItem] }));
        break;
      case 'settings':
        dispatch(userActions.setUserSettings({ payload: dialogFormState[selectedMenuItem] }));
        break;
    }

    const menuItem = menuItems.find((item) => item.code === selectedMenuItem);
    if (menuItem) {
      showToastMessage({ severity: 'success', message: menuItem.dialogProps.success_msg });
    }
    handleDialogClose();
  };

  const DrawerList = (
    <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer(false)}>
      <List>
        {menuItems.map((item, index) => (
          <ListItem key={item.code} disablePadding>
            <ListItemButton onClick={() => selectMenuItem(item.code)}>
              <ListItemIcon>
                {item.code === 'settings' ? <SettingsIcon /> :
                 index % 2 === 0 ? <PersonIcon /> : <HealthAndSafetyIcon />}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <div className={styles.headerMenu}>
      <div onClick={toggleDrawer(true)} className={styles.menu_button}>
        <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="100" height="100" viewBox="0 0 256 256">
          <g fill="#ffffff" fillRule="nonzero" stroke="none" strokeWidth="1" strokeLinecap="butt" strokeLinejoin="miter" strokeMiterlimit="10" strokeDasharray="" strokeDashoffset="0" fontFamily="none" fontWeight="none" fontSize="none" textAnchor="none" style={{ mixBlendMode: 'normal' }}>
            <g transform="scale(8.53333, 8.53333)">
              <path d="M3,7c-0.36064,-0.0051 -0.69608,0.18438 -0.87789,0.49587c-0.18181,0.3115 -0.18181,0.69676 0,1.00825c0.18181,0.3115 0.51725,0.50097 0.87789,0.49587h24c0.36064,0.0051 0.69608,-0.18438 0.87789,-0.49587c0.18181,-0.3115 0.18181,-0.69676 0,-1.00825c-0.18181,-0.3115 -0.51725,-0.50097 -0.87789,-0.49587zM3,14c-0.36064,-0.0051 -0.69608,0.18438 -0.87789,0.49587c-0.18181,0.3115 -0.18181,0.69676 0,1.00825c0.18181,0.3115 0.51725,0.50097 0.87789,0.49587h24c0.36064,0.0051 0.69608,-0.18438 0.87789,-0.49587c0.18181,-0.3115 -0.18181,0.69676 0,1.00825c-0.18181,0.3115 -0.51725,0.50097 -0.87789,0.49587zM3,21c-0.36064,-0.0051 -0.69608,0.18438 -0.87789,0.49587c-0.18181,0.3115 -0.18181,0.69676 0,1.00825c0.18181,0.3115 0.51725,0.50097 0.87789,0.49587h24c0.36064,0.0051 0.69608,-0.18438 0.87789,-0.49587c0.18181,-0.3115 0.18181,-0.69676 0,-1.00825c-0.18181,-0.3115 -0.51725,-0.50097 -0.87789,-0.49587z"></path>
            </g>
          </g>
        </svg>
      </div>
      <Drawer open={open} onClose={toggleDrawer(false)}>
        {DrawerList}
      </Drawer>
      <DialogWrapper
        open={isDialogOpen}
        title={menuItems.find((item) => item.code === selectedMenuItem)?.dialogProps?.title || ''}
        onClose={handleDialogClose}
        actions={[
          {
            type: "primary",
            text: "Cancel",
            invoke: handleDialogClose
          },
          {
            type: "primary",
            text: "Save",
            invoke: handleOnSave
          },
        ]}
      >
        {selectedMenuItem === 'profile' && <UserUpdate onChange={handleDialogFormChange} />}
        {selectedMenuItem === 'health_details' && <HealthUpdate onChange={handleDialogFormChange} />}
        {selectedMenuItem === 'settings' && <UserSettings onChange={handleDialogFormChange} />}
      </DialogWrapper>
    </div>
  );
};

export default Menu;
