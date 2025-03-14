import React, { useState, useMemo, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { IconButton, Menu, MenuItem, Badge } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { formatDistanceToNow } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import * as chatActions from '../../store/actionCreators/chatActionCreators';
import * as userActions from '../../store/actionCreators/userActionCreators';
import { RootState } from '../../store/types';
import styles from './Notification.module.css';
import { AppDispatch } from '../../store/store';
import { NotificationItem } from '../../types';


export const Notification: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const notifications = useSelector((state: RootState) => state.user.notifications);

  const unreadCount = useMemo(() =>
    notifications.filter(n => n.status === 'DELIVERED' || n.status === 'READY').length,
    [notifications]
  );

  useEffect(() => {
    if (notifications.length > 0) {
      const readyNotifications = notifications
        .filter(n => n.status === 'READY')
        .map(n => n.notificationId);

      if (readyNotifications.length > 0) {
        dispatch(userActions.updateNotificationStatus({
          notification_ids: readyNotifications,
          status: 'DELIVERED'
        }));
      }
    }
  }, [notifications, dispatch]);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);

    const unreadNotifications = notifications
      .filter(n => n.status !== 'VIEWED')
      .map(n => n.notificationId);

    if (unreadNotifications.length > 0) {
      dispatch(userActions.updateNotificationStatus({
        notification_ids: unreadNotifications,
        status: 'VIEWED'
      }));
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const formatTimeAgo = (timestamp: string): string => {
    return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
  };

  const handleNotificationClick = (notification: NotificationItem) => {
    if (notification.chatThreadId) {
      dispatch(chatActions.setCurrentChatThreadId(notification.chatThreadId, true));
      navigate(`/chat?id=${notification.chatThreadId}`);
      handleClose();
    }
  };

  return (
    <div className={styles.notificationComponent}>
      <IconButton onClick={handleClick}>
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {notifications.length === 0 ? (
          <MenuItem disabled>No notifications</MenuItem>
        ) : (
          notifications.map((notification) => (
            <MenuItem
              key={notification.notificationId}
              className={notification.status === 'VIEWED' ? styles.readNotification : styles.unreadNotification}
              onClick={() => handleNotificationClick(notification)}
            >
              <div>
                <div className={styles.notificationContent}>
                  <span className={styles.notificationTitle}>{notification.title}: </span>
                  {notification.content}
                </div>
                <div className={styles.notificationTime}>
                  {formatTimeAgo(notification.createdAt)}
                </div>
              </div>
            </MenuItem>
          ))
        )}
      </Menu>
    </div>
  );
};

export default Notification;
